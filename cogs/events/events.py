import discord
from discord.ext import commands
import random

class Events:
    def __init__(self, bot):
        self.bot = bot

    @bot.event(pass_context=True)
    async def on_message(self, ctx):
        """Parse and play with message"""
        await self.bot.say(ctx.message.clean_content)


def setup(bot):
    n = Events(bot)
    bot.add_cog(n)

