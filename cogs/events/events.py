import discord
from discord.ext import commands
import random

class Events:
    def __init__(self, bot):
        self.bot = bot

        @bot.event
        async def on_message(message):
            """Parse and play with message"""
            await bot.process_commands(message)
            await self.bot.say(ctx.message)


def setup(bot):
    n = Events(bot)
    bot.add_cog(n)

