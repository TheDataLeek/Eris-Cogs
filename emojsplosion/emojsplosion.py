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

    async def get_emojis(self, must_contain: str = ""):
        return [e for e in self.bot.emojis if must_contain in e.name]

    @commands.command(aliases=["emojsploj", "exploji"])
    async def emojsplosion(self, ctx: commands.Context, must_contain: str = ""):
        message: discord.Message = ctx.message

        if not message.reference:
            await ctx.send("Need to reply to a message!")
            return

        emojis = await self.get_emojis(must_contain=must_contain)

        channel: discord.Channel = ctx.channel
        referenced: discord.MessageReference = message.reference
        referenced_message: discord.Message = await channel.fetch_message(
            referenced.message_id
        )

        if len(emojis) > 20:
            emojis = random.sample(emojis, 20)

        for e in emojis:
            try:
                await referenced_message.add_reaction(e)
            except:
                pass
