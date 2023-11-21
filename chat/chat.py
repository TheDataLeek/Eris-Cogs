import asyncio
import re
import base64
import io
from pprint import pprint
from typing import Dict, List, Tuple, Union

import discord
import openai
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils import chat_formatting

BaseCog = getattr(commands, "Cog", object)


class Chat(BaseCog):
    def __init__(self, bot):
        self.bot: Red = bot
        self.openai_settings = None
        self.openai_token = None

    async def get_openai_token(self):
        self.openai_settings = await self.bot.get_shared_api_tokens("openai")
        self.openai_token = self.openai_settings.get("key", None)
        return self.openai_token

    @commands.command()
    async def rewind(self, ctx: commands.Context) -> None:
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        if not isinstance(channel, discord.Thread):
            await ctx.send("Chat command can only be used in an active thread! Please ask a question first.")
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
    async def chatas(self, ctx: commands.Context) -> None:
        """
        Very similar to [p]chat except anything encoded in backticks is treated as a system message. System messages
        are hoisted.
        """
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        thread_name = None

        message_without_command = ' '.join(message.content.split(' ')[1:])

        if not message_without_command:
            return

        if isinstance(channel, discord.TextChannel):
            query, system_messages = extract_system_messages_from_message(message_without_command)
            thread_name = " ".join(query.split(" ")[:5]) + "..."
            formatted_query = [
                *[
                    {
                        "role": "system",
                        "content": msg
                    }
                    for msg in system_messages
                ],
                {
                    "role": "user",
                    "name": author.display_name,
                    "content": [
                        {"type": "text", "text": query},
                        *[
                            {"type": "image_url", "image_url": {"url": attachment.url}}
                            for attachment in message.attachments
                        ],
                    ],
                }
            ]
        elif isinstance(channel, discord.Thread):
            formatted_query = []
            starter_message = channel.starter_message
            if starter_message is not None:
                starter_message_content_without_command = ' '.join(starter_message.content.split(' ')[1:])
                query, system_messages = extract_system_messages_from_message(starter_message_content_without_command)
                formatted_query = [
                    *[
                        {
                            "role": "system",
                            "content": msg
                        }
                        for msg in system_messages
                    ],
                    {
                        "role": "user",
                        "name": author.display_name,
                        "content": [
                            {"type": "text", "text": query},
                            *[
                                {"type": "image_url", "image_url": {"url": attachment.url}}
                                for attachment in message.attachments
                            ],
                        ],
                    }
                ]
            async for thread_message in channel.history(limit=100, oldest_first=True):
                if thread_message.author.bot:
                    formatted_query.append({
                        "role": "assistant",
                        "name": thread_message.author.display_name,
                        "content": [
                            {
                                "type": "text",
                                "text": thread_message.clean_content,
                            },
                        ],
                    })
                elif thread_message.clean_content.startswith(f"{prefix}chat"):
                    query, system_messages = extract_system_messages_from_message(thread_message.content)
                    # first, hoist all system messages to top of current message block
                    formatted_query += [
                        {
                            "role": "system",
                            "content": msg
                        }
                        for msg in system_messages
                    ]

                    # then we can add the current message
                    formatted_query.append({
                        "role": "user",
                        "name": thread_message.author.display_name,
                        "content": [
                            {
                                "type": "text",
                                "text": " ".join(
                                    w for w in thread_message.clean_content.split(" ") if w != f"{prefix}chat"
                                ),
                            },
                            *[
                                {"type": "image_url", "image_url": {"url": attachment.url}}
                                for attachment in thread_message.attachments
                            ],
                        ],
                    })
        else:
            return

        print(formatted_query)

        await self.query_openai(message, channel, thread_name, formatted_query)

    @commands.command()
    async def chat(self, ctx: commands.Context) -> None:
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        thread_name = None

        query = message.clean_content.split(' ')[1:]

        if not query:
            return

        if isinstance(channel, discord.TextChannel):
            formatted_query = " ".join(query)

            thread_name = " ".join(formatted_query.split(" ")[:5]) + "..."
            formatted_query = [
                {
                    "role": "user",
                    "name": author.display_name,
                    "content": [
                        {"type": "text", "text": formatted_query},
                        *[
                            {"type": "image_url", "image_url": {"url": attachment.url}}
                            for attachment in message.attachments
                        ],
                    ],
                }
            ]
        elif isinstance(channel, discord.Thread):
            formatted_query = []
            starter_message = channel.starter_message
            if starter_message is not None:
                message_without_command = ' '.join(starter_message.content.split(' ')[1:])
                formatted_query = [
                    {
                        "role": "user",
                        "name": author.display_name,
                        "content": [
                            {"type": "text", "text": message_without_command},
                            *[
                                {"type": "image_url", "image_url": {"url": attachment.url}}
                                for attachment in starter_message.attachments
                            ],
                        ],
                    }
                ]
            formatted_query += [
                {
                    "role": "assistant" if thread_message.author.bot else "user",
                    "name": thread_message.author.display_name,
                    "content": [
                        {
                            "type": "text",
                            "text": " ".join(
                                w for w in thread_message.clean_content.split(" ") if w != f"{prefix}chat"
                            ),
                        },
                        *[
                            {"type": "image_url", "image_url": {"url": attachment.url}}
                            for attachment in thread_message.attachments
                        ],
                    ],
                }
                async for thread_message in channel.history(limit=100, oldest_first=True)
                if thread_message.author.bot or thread_message.clean_content.startswith(f"{prefix}chat")
            ]
        else:
            return

        print(formatted_query)

        await self.query_openai(message, channel, thread_name, formatted_query)

    async def query_openai(self,
                           message: discord.Message,
                           channel: Union[discord.TextChannel, discord.Thread],
                           thread_name: str,
                           formatted_query: List[Dict]
                           ):
        token = await self.get_openai_token()
        try:
            response = await openai_query(formatted_query, token, model="gpt-4-vision-preview")
        except Exception as e:
            await channel.send(f"Something went wrong: {e}")
            return

        destination = channel
        if isinstance(channel, discord.TextChannel):
            thread: discord.Thread = await message.create_thread(name=thread_name)
            destination = thread

        for page in response:
            await destination.send(page)

    @commands.command()
    async def vibecheck(self, ctx: commands.Context) -> None:
        raw_query = ctx.message.clean_content.split(" ")[1:]

        if not raw_query:
            raw_query = "a random emoji".split(" ")

        channel: discord.abc.Messageable = ctx.channel

        formatted_query = " ".join(raw_query)
        formatted_query = [
            {
                "role": "system",
                "content": (
                    "You are a summarizing machine that accepts many types of input and provides back short output."
                    " You will be provided some input in the following user message and you will identify a"
                    " single emoji and a short phrase with heavy usage of emoji to capture the overall"
                    " feeling, emotion, and overall concept contained. This captured feeling should loosely align"
                    " with the input and your summation should be whimsical in a Gen-Z, Zillenial, 'Vibe-Based'"
                    " sort of way."
                ),
            },
            {"role": "user", "content": formatted_query},
        ]
        try:
            token = await self.get_openai_token()
            response = await openai_query(formatted_query, token, model="gpt-4", max_tokens=50)
            await channel.send(response[0])
        except Exception as e:
            await channel.send(f"Something went wrong: {e}")


async def openai_query(
        query: List[Dict], token: str, model="gpt-4-vision-preview", temperature=1, max_tokens=2000
) -> List[str]:
    loop = asyncio.get_running_loop()
    time_to_sleep = 1
    while True:
        if time_to_sleep > 1:
            raise TimeoutError("Tried too many times!")
        try:
            response: str = await loop.run_in_executor(
                None,
                lambda: openai_client_and_query(token, query, model, temperature, max_tokens),
            )
            break
        except Exception as e:
            print(e)
            await asyncio.sleep(time_to_sleep ** 2)
            time_to_sleep += 1

    response_lines = pagify_chat_result(response)

    return response_lines


def pagify_chat_result(response: str) -> List[str]:
    if len(response) <= 2000:
        return [response]

    # split on code
    code_expression = re.compile(r"(```(?:[^`]+)```)", re.IGNORECASE)
    split_by_code = code_expression.split(response)
    lines = []
    for line in split_by_code:
        if line.startswith('```'):
            if len(line) <= 2000:
                lines.append(line)
            else:
                codelines = list(chat_formatting.pagify(line))
                for i, subline in enumerate(codelines):
                    if i == 0:
                        lines.append(subline + '```')
                    elif i == len(codelines) - 1:
                        lines.append('```' + subline)
                    else:
                        lines.append('```' + subline + '```')
        else:
            lines += chat_formatting.pagify(line)

    return lines




def openai_client_and_query(token: str, messages: List[Dict], model: str, temperature: int, max_tokens: int):
    client = openai.OpenAI(api_key=token)
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    response = chat_completion.choices[0].message.content
    return response


def extract_system_messages_from_message(message: str) -> Tuple[str, List[str]]:
    # extract the system messages
    # https://regex101.com/r/5VTsQ7/1
    system_message_expression = re.compile(r"(`+)([^`]+)\1", re.IGNORECASE)

    system_messages = [msg for tick, msg in
                       system_message_expression.findall(message)]

    # now remove them
    message_without_system, _ = system_message_expression.subn('', message)
    query = message_without_system.strip()

    return query, system_messages
