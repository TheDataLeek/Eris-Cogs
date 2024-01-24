from __future__ import annotations

import asyncio
import json
from PIL import Image
import re
import base64
import io
from pprint import pprint
from typing import Dict, List, Tuple, Union

import discord
import openai
from redbot.core import commands, data_manager
from redbot.core.bot import Red
from redbot.core.utils import chat_formatting

BaseCog = getattr(commands, "Cog", object)


class Chat(BaseCog):
    def __init__(self, bot):
        self.bot: Red = bot
        self.openai_settings = None
        self.openai_token = None
        self.data_dir = data_manager.bundled_data_path(self)

    async def get_openai_token(self):
        self.openai_settings = await self.bot.get_shared_api_tokens("openai")
        self.openai_token = self.openai_settings.get("key", None)
        return self.openai_token

    async def get_prefix(self, ctx: commands.Context) -> str:
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]
        return prefix

    @commands.command()
    async def rewind(self, ctx: commands.Context) -> None:
        prefix = await self.get_prefix(ctx)

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        if not isinstance(channel, discord.Thread):
            await ctx.send(
                "Chat command can only be used in an active thread! Please ask a question first."
            )
            return

        found_bot_response = False
        found_last_bot_response = False
        found_chat_input = False
        async for thread_message in channel.history(limit=100, oldest_first=False):
            try:
                if thread_message.author.bot:
                    await thread_message.delete()
                    found_bot_response = True
                elif found_bot_response:
                    found_last_bot_response = True

                if thread_message.clean_content.startswith(f"{prefix}chat"):
                    await thread_message.delete()
                    found_chat_input = True

                if found_chat_input and found_bot_response and found_last_bot_response:
                    break
            except Exception as e:
                break

        await message.delete()

    @commands.command()
    async def tarot(self, ctx: commands.Context) -> None:
        thread_name, formatted_query = await self.extract_chat_history_and_format(ctx)
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        tarot_guide = (self.data_dir / "tarot_guide.txt").read_text()
        lines_to_include = [(406, 3744)]
        split_guide = tarot_guide.split("\n")
        passages = [
            "\n".join(split_guide[start : end + 1]) for start, end in lines_to_include
        ]

        formatted_query = [
            {
                "role": "system",
                "content": (
                    "You are to intepret the user-provided tarot reading below using the provided"
                    f"reference guide. Please ask for clarification when needed, "
                    "and allow for non-standard layouts to be described. Additionally if users provide images "
                    "please read which cards are out, taking note of arrangement and orientation and provide the "
                    "full reading in either case."
                ),
            },
            *[{"role": "system", "content": passage} for passage in passages],
            *formatted_query,
        ]

        await self.query_openai(
            message, channel, thread_name, formatted_query, model="gpt-3.5-turbo"
        )

    @commands.command()
    async def chatas(self, ctx: commands.Context) -> None:
        """
        Very similar to [p]chat except anything encoded in backticks is treated as a system message. System messages
        are hoisted.
        """
        prefix = await self.get_prefix(ctx)

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        thread_name = None

        message_without_command = " ".join(message.content.split(" ")[1:])

        if not message_without_command:
            return

        if isinstance(channel, discord.TextChannel):
            query, system_messages = extract_system_messages_from_message(
                message_without_command
            )
            thread_name = " ".join(query.split(" ")[:5]) + "..."
            formatted_query = [
                *[{"role": "system", "content": msg} for msg in system_messages],
                {
                    "role": "user",
                    "name": author.name,
                    "content": [
                        {"type": "text", "text": query},
                        *[
                            await format_attachment(attachment)
                            for attachment in message.attachments
                        ],
                    ],
                },
            ]
        elif isinstance(channel, discord.Thread):
            formatted_query = []
            starter_message = channel.starter_message
            if starter_message is not None:
                starter_message_content_without_command = " ".join(
                    starter_message.content.split(" ")[1:]
                )
                query, system_messages = extract_system_messages_from_message(
                    starter_message_content_without_command
                )
                formatted_query = [
                    *[{"role": "system", "content": msg} for msg in system_messages],
                    {
                        "role": "user",
                        "name": author.name,
                        "content": [
                            {"type": "text", "text": query},
                            *[
                                await format_attachment(attachment)
                                for attachment in message.attachments
                            ],
                        ],
                    },
                ]
            async for thread_message in channel.history(limit=100, oldest_first=True):
                if thread_message.author.bot:
                    formatted_query.append(
                        {
                            "role": "assistant",
                            "name": thread_message.author.name,
                            "content": [
                                {
                                    "type": "text",
                                    "text": thread_message.clean_content,
                                },
                            ],
                        }
                    )
                elif thread_message.clean_content.startswith(f"{prefix}chat"):
                    query, system_messages = extract_system_messages_from_message(
                        thread_message.content
                    )
                    # first, hoist all system messages to top of current message block
                    formatted_query += [
                        {"role": "system", "content": msg} for msg in system_messages
                    ]

                    # then we can add the current message
                    formatted_query.append(
                        {
                            "role": "user",
                            "name": thread_message.author.name,
                            "content": [
                                {
                                    "type": "text",
                                    "text": " ".join(
                                        w
                                        for w in thread_message.clean_content.split(" ")
                                        if w != f"{prefix}chat"
                                    ),
                                },
                                *[
                                    await format_attachment(attachment)
                                    for attachment in thread_message.attachments
                                ],
                            ],
                        }
                    )
        else:
            return

        await self.query_openai(message, channel, thread_name, formatted_query)

    async def extract_chat_history_and_format(self, ctx: commands.Context):
        prefix = await self.get_prefix(ctx)

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        thread_name = None

        query = message.clean_content.split(" ")[1:]

        if not query:
            return

        if isinstance(channel, discord.TextChannel):
            formatted_query = " ".join(query)

            thread_name = " ".join(formatted_query.split(" ")[:5]) + "..."
            formatted_query = [
                {
                    "role": "user",
                    "name": author.name,
                    "content": [
                        {"type": "text", "text": formatted_query},
                        *[
                            await format_attachment(attachment)
                            for attachment in message.attachments
                        ],
                    ],
                }
            ]
        elif isinstance(channel, discord.Thread):
            formatted_query = []
            starter_message = channel.starter_message
            if starter_message is not None:
                message_without_command = " ".join(
                    starter_message.content.split(" ")[1:]
                )
                formatted_query = [
                    {
                        "role": "user",
                        "name": author.name,
                        "content": [
                            {"type": "text", "text": message_without_command},
                            *[
                                await format_attachment(attachment)
                                for attachment in starter_message.attachments
                            ],
                        ],
                    }
                ]
            formatted_query += [
                {
                    "role": "assistant" if thread_message.author.bot else "user",
                    "name": thread_message.author.name,
                    "content": [
                        {
                            "type": "text",
                            "text": " ".join(
                                w
                                for w in thread_message.clean_content.split(" ")
                                if not w.startswith(".")
                            ),
                        },
                        *[
                            {"type": "text", "text": json.dumps(embed.to_dict())}
                            for embed in thread_message.embeds
                        ],
                        *[
                            await format_attachment(attachment)
                            for attachment in thread_message.attachments
                        ],
                    ],
                }
                async for thread_message in channel.history(
                    limit=100, oldest_first=True
                )
                if thread_message.author.bot
                or thread_message.clean_content.startswith(".")
            ]
        else:
            return None

        return thread_name, formatted_query

    @commands.command()
    async def chat(self, ctx: commands.Context) -> None:
        thread_name, formatted_query = await self.extract_chat_history_and_format(ctx)
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        await self.query_openai(message, channel, thread_name, formatted_query)

    @commands.command()
    async def image(self, ctx: commands.Context):
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        prompt_words = [w for i, w in enumerate(message.content.split(" ")) if i != 0]
        prompt: str = " ".join(prompt_words)
        thread_name = " ".join(prompt_words[:5]) + " image"
        attachment = None
        attachments: list[discord.Attachment] = [
            m for m in message.attachments if m.width
        ]
        if len(attachments) > 0:
            attachment: discord.Attachment = attachments[0]
        elif prompt == "":
            return

        await self.query_openai(
            message,
            channel,
            thread_name,
            prompt,
            attachment=attachment,
            image_api=True,
        )

    async def query_openai(
        self,
        message: discord.Message,
        channel: discord.TextChannel | discord.Thread,
        thread_name: str,
        formatted_query: str | list[dict],
        attachment: discord.Attachment = None,
        image_api: bool = False,
        model: str = "gpt-4-vision-preview",
    ):
        token = await self.get_openai_token()
        channel_name = "a thread and no further warnings are needed"
        if isinstance(channel, discord.TextChannel):
            channel_name = f"#{channel.name}"
        system_prefix = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are a helpful robot user named Snek. "
                            "Users interact with you on the Discord messaging platform through messages "
                            "prefixed by `.`. To call ChatGPT, users prefix their messages with `.chat` and then "
                            "provide a query. Users should be using the #bot, #bots, or any similarly named channel or "
                            "a thread for all messages. If the current channel is not any of those, or in a thread, "
                            "please remind the user that their queries should be redirected to those locations. "
                            f"Our current location is {channel_name}. If we're in an appropriate channel, please don't "
                            "restate this policy"
                        ),
                    }
                ],
            }
        ]
        kwargs = {
            "model": model,
            "temperature": 1,
            "max_tokens": 2000,
        }
        try:
            if image_api:
                kwargs = {
                    "n": 1,
                    "model": "dall-e-2",
                    "response_format": "b64_json",
                    "size": "1024x1024",
                }
                if attachment is not None:  # then it's an edit
                    buf = io.BytesIO()
                    await attachment.save(buf)
                    buf.seek(0)
                    input_image = Image.open(buf)
                    input_image = input_image.resize((1024, 1024))
                    input_image_buffer = io.BytesIO()
                    input_image.save(input_image_buffer, format="png")
                    input_image_buffer.seek(0)
                    kwargs["image"] = input_image_buffer.read()

                    # mask = io.BytesIO()
                    # mask_image = Image.new('RGBA', (1024, 1024))
                    # mask_image.save(mask, format='png')
                    # mask.seek(0)
                    # kwargs['mask'] = mask.read()
                else:
                    style = None
                    if "vivid" in formatted_query:
                        style = "vivid"
                    elif "natural" in formatted_query:
                        style = "natural"
                    kwargs = {
                        **kwargs,
                        **{
                            "model": "dall-e-3",
                            "quality": "hd",
                            "style": style,
                        },
                    }
                response = await openai_query(formatted_query, token, **kwargs)
            else:
                response = await openai_query(
                    system_prefix + formatted_query, token, **kwargs
                )
        except Exception as e:
            await channel.send(f"Something went wrong: {e}")
            return

        destination = channel
        if isinstance(channel, discord.TextChannel):
            thread: discord.Thread = await message.create_thread(name=thread_name)
            destination = thread

        if isinstance(response, list):
            for page in response:
                await destination.send(page)
        else:
            filename = thread_name.replace(" ", "_") + ".png"
            await destination.send(file=discord.File(response, filename=filename))


async def openai_query(
    query: List[Dict], token: str, **kwargs
) -> list[str] | io.BytesIO:
    loop = asyncio.get_running_loop()
    time_to_sleep = 1
    exception_string = None
    while True:
        if time_to_sleep > 1:
            print(exception_string)
            raise TimeoutError(exception_string)
        try:
            response: str | io.BytesIO = await loop.run_in_executor(
                None, lambda: openai_client_and_query(token, query, **kwargs)
            )
            break
        except Exception as e:
            exception_string = str(e)
            await asyncio.sleep(time_to_sleep**2)
            time_to_sleep += 1

    if isinstance(response, str):
        return pagify_chat_result(response)

    return response


def pagify_chat_result(response: str) -> list[str]:
    if len(response) <= 2000:
        return [response]

    # split on code
    code_expression = re.compile(r"(```(?:[^`]+)```)", re.IGNORECASE)
    split_by_code = code_expression.split(response)
    lines = []
    for line in split_by_code:
        if line.startswith("```"):
            if len(line) <= 2000:
                lines.append(line)
            else:
                codelines = list(chat_formatting.pagify(line))
                for i, subline in enumerate(codelines):
                    if i == 0:
                        lines.append(subline + "```")
                    elif i == len(codelines) - 1:
                        lines.append("```" + subline)
                    else:
                        lines.append("```" + subline + "```")
        else:
            lines += chat_formatting.pagify(line)

    return lines


def openai_client_and_query(
    token: str, messages: str | list[dict], **kwargs
) -> str | io.BytesIO:
    client = openai.OpenAI(api_key=token)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if kwargs["model"].startswith("dall"):
        if "image" in kwargs:
            images = client.images.create_variation(**kwargs)
        else:
            images = client.images.generate(prompt=messages, **kwargs)
        encoded_image = images.data[0].b64_json
        image = base64.b64decode(encoded_image)
        buf = io.BytesIO()
        buf.write(image)
        buf.seek(0)
        response = buf
    else:
        chat_completion = client.chat.completions.create(
            messages=messages,
            **kwargs,
        )
        response = chat_completion.choices[0].message.content
    return response


def extract_system_messages_from_message(message: str) -> Tuple[str, List[str]]:
    # extract the system messages
    # https://regex101.com/r/5VTsQ7/1
    system_message_expression = re.compile(r"(`+)([^`]+)\1", re.IGNORECASE)

    system_messages = [msg for tick, msg in system_message_expression.findall(message)]

    # now remove them
    message_without_system, _ = system_message_expression.subn("", message)
    query = message_without_system.strip()

    return query, system_messages


async def format_attachment(attachment: discord.Attachment) -> dict:
    mimetype: str = attachment.content_type.lower()
    filename: str = attachment.filename.lower()
    formatted_attachment = {"type": "text", "text": "<MISSING ATTACHMENT>"}
    permitted_extensions = [
        "txt",
        "text",
        "json",
        "py",
        "md",
        "c",
        "h",
        "cpp",
        "hpp",
        "java",
        "js",
        "ts",
        "tsx",
        "html",
        "css",
        "scss",
        "xml",
    ]
    has_valid_extension = any([filename.endswith(ext) for ext in permitted_extensions])
    text = None
    if has_valid_extension or "text" in mimetype:  # if it's text
        buf = io.BytesIO()
        await attachment.save(buf)
        buf.seek(0)
        text = buf.read().decode("utf-8")
        formatted_attachment = {"type": "text", "text": text}
    elif attachment.width:  # then it's an image
        formatted_attachment = {
            "type": "image_url",
            "image_url": {"url": attachment.url},
        }
    if text is None:
        print(formatted_attachment)
    else:
        print(text[:25] + "..." + text[-25:])
    # otherwise it's not supported
    return formatted_attachment
