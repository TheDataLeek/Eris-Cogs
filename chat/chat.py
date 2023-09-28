import io
import base64
from typing import List, Dict, Union
import asyncio

from redbot.core import commands
from redbot.core.utils import chat_formatting, bounded_gather
import discord
import openai

BaseCog = getattr(commands, "Cog", object)


class Chat(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_settings = None
        self.openai_token = None

    async def get_openai_token(self):
        self.openai_settings = await self.bot.get_shared_api_tokens("openai")
        self.openai_token = self.openai_settings.get("key", None)
        return self.openai_token

    @commands.command()
    async def image(self, ctx: commands.Context):
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
                response: Dict = await loop.run_in_executor(None, lambda: openai.Image.create(
                    prompt=formatted_query,
                    n=1,
                    size='1024x1024',
                    response_format='b64_json'
                ))
                break
            except openai.error.RateLimitError:
                await asyncio.sleep(time_to_sleep**2)
                time_to_sleep += 1
            except openai.error.ServiceUnavailableError:
                await asyncio.sleep(time_to_sleep**2)
                time_to_sleep += 1
            except Exception as e:
                await ctx.send(f"Oops, you did something wrong! {e}")
                return

        image = response['data'][0]['b64_json'].encode()
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
        query = ctx.message.clean_content.split(" ")[1:]

        if not query:
            return

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        thread_name = None

        if isinstance(channel, discord.TextChannel):
            formatted_query = " ".join(query)
            openai_query = [{"role": "user", "content": formatted_query}]
            thread_name = formatted_query[:15] + '...'
        elif isinstance(channel, discord.Thread):
            history = [message async for message in channel.history(limit=100)]
            history = [
                {
                    "role": 'system' if thread_message.author.bot else 'user',
                    'content': ' '.join(w for w in thread_message.clean_content.split(' ') if w != '.chat')
                    # todo: prefix
                }
                for thread_message in history
                if thread_message.author.bot or thread_message.clean_content.startswith('.chat')
            ]
            openai_query = history
        else:
            return

        loop = asyncio.get_running_loop()
        openai.api_key = await self.get_openai_token()

        time_to_sleep = 1
        while True:
            try:
                chat_completion: Dict = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
                    # model="gpt-3.5-turbo",
                    model="gpt-4",
                    messages=openai_query,
                    temperature=1,
                    max_tokens=2000
                ))
                break
            except openai.error.RateLimitError:
                await asyncio.sleep(time_to_sleep**2)
                time_to_sleep += 1
            except openai.error.ServiceUnavailableError:
                await asyncio.sleep(time_to_sleep**2)
                time_to_sleep += 1
            except Exception as e:
                await ctx.send(f"Oops, you did something wrong! {e}")
                return

        if isinstance(channel, discord.TextChannel):
            try:
                response = chat_completion['choices'][0]['message']['content']
                thread: discord.Thread = await message.create_thread(name=thread_name)
                if len(response) < 1999:
                    await thread.send(response)
                else:
                    for page in chat_formatting.pagify(response, delims=['\n'], page_length=1250):
                        await thread.send(page)
            except Exception as e:
                raise
        elif isinstance(channel, discord.Thread):
            try:
                response = chat_completion['choices'][0]['message']['content']
                if len(response) < 1999:
                    await channel.send(response)
                else:
                    for page in chat_formatting.pagify(response, delims=[' ', '\n'], page_length=1500):
                        await channel.send(page)
            except Exception as e:
                raise

    @commands.command()
    async def vibecheck(self, ctx: commands.Context) -> None:
        query = ctx.message.clean_content.split(" ")[1:]

        if not query:
            query = "a random emoji".split(" ")

        channel: discord.abc.Messageable = ctx.channel

        formatted_query = " ".join(query)
        openai_query = [{
            "role": "user",
            "content": ("Please provide a single word or a single emoji response that summarizes the emotion, "
                        "feeling, and overall happiness contained in the following message in a loosely-defined "
                        f"vibe-based sort of way: {formatted_query}")
        }]

        loop = asyncio.get_running_loop()
        openai.api_key = await self.get_openai_token()

        time_to_sleep = 1
        while True:
            try:
                chat_completion: Dict = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
                    # model="gpt-3.5-turbo",
                    model="gpt-4",
                    messages=openai_query,
                    temperature=1,
                    max_tokens=2000
                ))
                break
            except openai.error.RateLimitError:
                await asyncio.sleep(time_to_sleep**2)
                time_to_sleep += 1
            except openai.error.ServiceUnavailableError:
                await asyncio.sleep(time_to_sleep**2)
                time_to_sleep += 1
            except Exception as e:
                await ctx.send(f"Oops, you did something wrong! {e}")
                return

        try:
            response = chat_completion['choices'][0]['message']['content']
            await channel.send(response)
        except Exception as e:
            raise
