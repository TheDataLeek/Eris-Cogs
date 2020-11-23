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

            wiggler_id = 605433851707392033
            dogbless = 687144702394499293
            dansen = 702322986765516802
            bongo = 559949424034316288

            emojis = {e.id: e for e in self.bot.emojis}
            if author.id == 405152630055108619 and random.random() <= 0.5:
                await message.add_reaction(emojis[wiggler_id])
                return

            if author.id == 159771760508534784 and random.random() <= 0.01:
                await message.add_reaction(emojis[dogbless])
                return

            if author.id == 142431859148718080 and random.random() <= 0.05:
                await message.add_reaction(emojis[dansen])
                return

            # nikki
            if author.id == 287464881081548810 and random.random() <= 0.1:
                await message.add_reaction(emojis[bongo])
                return


