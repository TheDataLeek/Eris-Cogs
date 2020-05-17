import re
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)

RETYPE = type(re.compile("a"))


class NoFuckYou(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance

        self.fuck_you_regex: RETYPE = re.compile(
            "f[uck]{,3} [^ ]+", flags=re.IGNORECASE
        )

        self.bot.add_listener(self.no_fuck_you, "on_message")

    async def no_fuck_you(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            keyword_in_message: bool = bool(
                self.fuck_you_regex.search(message.clean_content.lower())
            )

            if not allowed or not keyword_in_message:
                return

            await ctx.send("No fuck you")

            await self.log_last_message(ctx, message)
