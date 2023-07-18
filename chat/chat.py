import io
import os
from urllib import parse
from pprint import pprint as pp
import json
from typing import List, Dict

from redbot.core import commands
import discord
import aiohttp
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
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
    async def chat(self, ctx: commands.Context, *query: str):
        channel: discord.TextChannel = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        # chunk: List[discord.Message] = [message async for message in channel.history(limit=50)]
        # formatted_chunk = '\n'.join([
        #     f"@{message.author.display_name}: {message.clean_content}"
        #     for message in chunk
        # ])
        # # todo: dynamically find bot's name
        # openai_query = (
        #     "You are the robot user named Snek who is mischievous and naughty. "
        #     "You have a long history of playing pranks on everyone mentioned in the following chat logs. "
        #     "Given these logs, please provide an appropriate response as your Snek persona."
        #     f"\n{formatted_chunk}"
        # )
        if not query:
            return
        openai_query = " ".join(query)
        openai.api_key = await self.get_openai_token()
        chat_completion: Dict = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                             messages=[{"role": "user", "content": openai_query}],
                                                             temperature=1.5)
        try:
            response = chat_completion['choices'][0]['message']['content']
            thread: discord.Thread = await message.create_thread(openai_query[:15] + '...')
            await thread.send(response)
        except Exception as e:
            raise
