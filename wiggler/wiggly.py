# stdlib
import random
import re

from typing import Optional

# third party
import discord
from redbot.core import commands, bot, checks, Config

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


class Wiggle(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.config = Config.get_conf(
            self,
            identifier=8766782347657182931290319283,
            force_registration=True,
            cog_name="wiggle",
        )

        default_guild = {
            "wiggle": {},
        }
        self.config.register_guild(**default_guild)

        self.bot.add_listener(self.wiggle_handler, "on_message")

    @commands.group()
    async def wiggle(self, ctx: commands.Context):
        pass

    @wiggle.command()
    async def set(self, ctx: commands.Context, emoji: Optional[discord.Emoji]=None):
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            if emoji is None:
                del wigglelist[ctx.author.id]
            else:
                wigglelist[ctx.author.id] = emoji

    async def wiggle_handler(self, message: discord.message):
        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock(), self.config.guild(ctx.guild).wiggle() as wigglelist:
            author = ctx.message.author
            allowed: bool = await self.allowed(ctx, message)
            allowed &= random.random() <= 0.05
            allowed &= author.id in wigglelist

            await message.add_reaction(wigglelist[author.id])
