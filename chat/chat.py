import asyncio
import base64
import io
from pprint import pprint
from typing import Dict, List

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
    async def image(self, ctx: commands.Context):
        return
        query = ctx.message.clean_content.split(" ")[1:]

        if not query:
            return

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        formatted_query = " ".join(query)
        filename = "_".join(query[:5]) + ".png"
        openai.api_key = await self.get_openai_token()
        loop = asyncio.get_running_loop()

        time_to_sleep = 1
        while True:
            try:
                response: Dict = await loop.run_in_executor(
                    None,
                    lambda: openai.Image.create(
                        prompt=formatted_query, model="dall-e-3", n=1, size="1024x1024", response_format="b64_json"
                    ),
                )
                break
            except openai.error.RateLimitError:
                await asyncio.sleep(time_to_sleep ** 2)
                time_to_sleep += 1
            except openai.error.ServiceUnavailableError:
                await asyncio.sleep(time_to_sleep ** 2)
                time_to_sleep += 1
            except Exception as e:
                await ctx.send(f"Oops, you did something wrong! {e}")
                return

        image = response["data"][0]["b64_json"].encode()
        buf = io.BytesIO()
        buf.write(base64.b64decode(image))
        buf.seek(0)
        if isinstance(channel, discord.TextChannel):
            thread: discord.Thread = await message.create_thread(name=filename)
            await thread.send(file=discord.File(buf, filename=filename))
        elif isinstance(channel, discord.Thread):
            await channel.send(file=discord.File(buf, filename=filename))

    @commands.command()
    async def chat(self, ctx: commands.Context) -> None:
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]

        query = ctx.message.clean_content.split(" ")[1:]

        if not query:
            return

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        thread_name = None

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
            formatted_query = [
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
                    " single emoji or a short phrase with heavy usage of emoji to capture the overall"
                    " feeling, emotion, and overall concept contained. This captured feeling should loosely align"
                    " with the input and your summation should be whimsical in a Gen-Z, Zillenial, 'Vibe-Based'"
                    " sort of way."
                ),
            },
            {"role": "user", "content": formatted_query},
        ]
        try:
            token = await self.get_openai_token()
            response = await openai_query(formatted_query, token, model="gpt4", max_tokens=50)
            await channel.send(response[0])
        except Exception as e:
            await channel.send(f"Something went wrong: {e}")


async def openai_query(
    query: List[Dict], token: str, model="gpt-4-vision-preview", temperature=1, max_tokens=2000
) -> List[Dict]:
    loop = asyncio.get_running_loop()
    time_to_sleep = 1
    while True:
        if time_to_sleep > 3:
            raise TimeoutError("Tried too many times!")
        try:
            response: Dict = await loop.run_in_executor(
                None,
                lambda: openai_client_and_query(token, query, model, temperature, max_tokens),
            )
            break
        except Exception as e:
            print(e)
            await asyncio.sleep(time_to_sleep ** 2)
            time_to_sleep += 1

    if len(response) < 1999:
        response_list = [response]
    else:
        response_list = [page for page in chat_formatting.pagify(response, delims=["\n"], page_length=1250)]

    return response_list


def openai_client_and_query(token: str, messages: List[Dict], model: str, temperature: int, max_tokens: int):
    client = openai.OpenAI(api_key=token)
    chat_completion = client.completions.create(
        prompt=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    response = chat_completion.choices[0].text
    return response
