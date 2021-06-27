import re
import random
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)
RETYPE = type(re.compile("a"))


class JustMetHer(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance
        # https://regex101.com/r/FQfm4m/1/
        self.searchpattern: RETYPE = re.compile(
                r"\b(\w{3,})[eiouya]re?\b", flags=re.IGNORECASE
        )

        self.bot.add_listener(self.met_her, "on_message")

    async def met_her(self, message: discord.Message):
        clean_message: str = message.clean_content.lower()
        matched = self.searchpattern.search(clean_message)
        activated: bool = matched and (random.random() < 0.5)
        if not activated:
            return

        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return

            phrase = ["I hardly knew 'er!", "I just met 'er!"]
            await ctx.send(
                f"{matched.group(1)}'r? {random.choice(phrase)}", reference=message
            )
            await self.log_last_message(ctx, message)
