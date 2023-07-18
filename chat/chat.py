import io
from typing import List, Dict, Union

from redbot.core import commands
from redbot.core.utils import chat_formatting
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
    async def image(self, ctx: commands.Context, *query: str):
        if not query:
            return
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        formatted_query = " ".join(query)
        filename = "_".join(query[:5]) + ".png"
        openai.api_key = await self.get_openai_token()
        response: Dict = openai.Image.create(
            prompt=formatted_query,
            n=1,
            size='1024x1024',
            response_format='b64_json'
        )
        image = response['data'][0]['b64_json']
        buf = io.BytesIO()
        buf.write(image)
        buf.seek(0)
        if isinstance(channel, discord.TextChannel):
            thread: discord.Thread = await message.create_thread(name=filename)
            await thread.send(file=discord.File(buf, filename=filename))
        elif isinstance(channel, discord.Thread):
            await channel.send(file=discord.File(buf, filename=filename))

    @commands.command()
    async def chat(self, ctx: commands.Context, *query: str) -> None:
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
            ]
            openai_query = history
        else:
            return

        openai.api_key = await self.get_openai_token()
        chat_completion: Dict = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="gpt-4",
            messages=openai_query,
            temperature=1.25,
            max_tokens=2000
        )

        if isinstance(channel, discord.TextChannel):
            try:
                response = chat_completion['choices'][0]['message']['content']
                thread: discord.Thread = await message.create_thread(name=thread_name)
                if len(response) < 1999:
                    await thread.send(response)
                else:
                    for page in chat_formatting.pagify(response, delims=[' ', '\n'], page_length=1500):
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
