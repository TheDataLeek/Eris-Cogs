import re
import discord
import random
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)

RETYPE = type(re.compile("a"))


class NoFuckYou(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance

        self.fuck_you_regex: RETYPE = re.compile(
            r"\bf[uck]{,3} \b", flags=re.IGNORECASE
        )
        self.bot.add_listener(self.no_fuck_you, "on_message")

    async def no_fuck_you(self, message: discord.Message):
        keyword_in_message: bool = bool(
            self.fuck_you_regex.search(message.clean_content)
        )
        if not keyword_in_message:
            return

        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return

            if random.random() <= 0.5:
                return

            await ctx.send("No fuck you")

            await self.log_last_message(ctx, message)
