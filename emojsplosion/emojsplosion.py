# stdlib
import random
import re

from typing import Optional, List

# third party
import discord
from redbot.core import commands, bot, checks, Config
from redbot.core.utils import embed
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

BaseCog = getattr(commands, "Cog", object)


class EmojSplosion(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.emojis = {}

    async def get_emojis(self):
        self.emojis = [e for e in self.bot.emojis]

    @commands.command()
    async def emojsplosion(
        self, ctx: commands.Context
    ):
        message: discord.Message = ctx.message
        await self.get_emojis()

        if not message.reference:
            await ctx.send("Need to reply to a message!")
            return

        channel: discord.Channel = ctx.channel
        referenced: discord.MessageReference = message.reference
        referenced_message: discord.Message = await channel.fetch_message(referenced.message_id)

        emojis = random.sample(self.emojis, 20)
        for e in emojis:
            # try:
            await referenced_message.add_reaction(e)
            # except:
            #     pass
