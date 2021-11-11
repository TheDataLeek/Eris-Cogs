import re
import random
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)
RETYPE = type(re.compile("a"))


class Venmo(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance
        self.bot.add_listener(self.venmo, "on_message")

    async def venmo(self, message: discord.Message):
        clean_message: str = message.clean_content.lower()
        matched = ('venmo' in clean_message) or ('paypal' in clean_message)

        if not matched:
            return

        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return
            await ctx.send(
                    (
                        "Hey! I’ve been using Cash App to send money and spend using the Cash Card. "
                        "Try it using my code and you’ll get $5. VPMBXJW https://cash.app/app/VPMBXJW"
                    ),
                    reference=message
            )
            await self.log_last_message(ctx, message)
