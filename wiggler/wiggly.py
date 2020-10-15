# stdlib
import random
import re

# third party
import discord
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

            emojis = {e.name: e for e in message.guild.emojis}
            if str(author.id) == '405152630055108619' and random.random() <= 0.5:
                await message.add_reaction(emojis['wiggler'])
                return

            if str(author.id) == '159771760508534784' and random.random() <= 0.01:
                await message.add_reaction(emojis['dogbless'])
                return

            if str(author.id) == '142431859148718080' and random.random() <= 0.05:
                await message.add_reaction(emojis['caramelldansen'])
                return


