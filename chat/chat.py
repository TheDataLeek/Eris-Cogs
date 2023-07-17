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
    async def chat(self, ctx: commands.Context):
        channel: discord.TextChannel = ctx.channel
        chunk: List[discord.Message] = [message async for message in channel.history(limit=10)]
        formatted_chunk = '\n\n'.join([
            f"{message.author.display_name}: {message.clean_content}"
            for message in chunk
        ])
        # todo: dynamically find bot's name
        openai_query = (
            "You are the robot user named Snek. "
            "Given the following chat logs, please provide an appropriate response and "
            "answer any questions that might have been asked."
            f"\n\n{formatted_chunk}"
        )
        openai.api_key = await self.get_openai_token()
        chat_completion: Dict = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                             messages=[{"role": "user", "content": openai_query}])
        try:
            response = chat_completion['choices'][0]['message']
            await ctx.channel.send(response)
        except Exception as e:
            await ctx.channel.send("Something went wrong!")
