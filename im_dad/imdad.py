import re
import random
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)
RETYPE = type(re.compile("a"))


class ImDad(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance
        self.searchpattern: RETYPE = re.compile(
            r"(?<![a-z])i'?m ([^\.\?\!,\n\r]+)", flags=re.IGNORECASE
        )

        self.bot.add_listener(self.imdad, "on_message")

    async def imdad(self, message: discord.Message):
        clean_message: str = message.clean_content.lower()
        matched = self.searchpattern.search(clean_message)
        activated: bool = matched and (random.random() < 0.25)
        if not activated:
            return

        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return

            whoami = ["Dad", "Mom", "Snek"]
            await ctx.send(
                f"Hi {matched.group(1)} I'm {random.choice(whoami)}", reference=message
            )
            await self.log_last_message(ctx, message)
