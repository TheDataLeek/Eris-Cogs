# stdlib
import random
import re

# third party
from redbot.core import commands, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


class Wiggle(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance
        self.bot.add_listener(self.wiggle, 'on_message')

    async def wiggle(self, message: discord.message):
        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            author: discord.Member = message.author

            if str(author.id) != '405152630055108619':
                return

            emojis = {e.name: e for e in message.guild.emojis}
            await message.add_reaction(emojis['wiggler'])

