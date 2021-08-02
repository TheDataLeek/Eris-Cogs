import random
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)

VOICELINES = [
    "Rock on!",
    "Rock and stone.. Yeeaaahhh!",
    "Rock and stone forever!",
    "ROCK... AND... STONE!",
    "Rock and stone!",
    "For rock and stone!",
    "We are unbreakable!",
    "Rock and roll!",
    "Rock and roll and stone!",
    "That's it lads! Rock and stone!",
    "Like that! Rock and stone!",
    "Yeaahhh! Rock and stone!",
    "None can stand before us!",
    "Rock solid!",
    "Come on guys! Rock and stone!",
    "If you don't rock and stone, you ain't comin' home!",
    "We fight for rock and stone!",
    "We rock!",
    "Rock and stone everyone!",
    "Stone!",
    "Rock and stone in the heart!",
    "For teamwork!",
    "Did I hear a rock and stone?",
    "Stone and rock!",
    "Stone and rock! Oh wait...",
    "Yeah yeah, rock and stone.",
]


class RockAndStone(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance

        self.bot.add_listener(self.rock_and_stone, "on_message")

    async def rock_and_stone(self, message: discord.Message):
        clean_message: str = message.clean_content.lower()
        keyword_in_message: bool = ("rock" in clean_message) and (
            "stone" in clean_message
        )
        if not keyword_in_message:
            return

        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return

            voiceline = random.choice(VOICELINES)
            await ctx.send(f"⛏️ {voiceline} ⛏️", reference=message)
            await self.log_last_message(ctx, message)
