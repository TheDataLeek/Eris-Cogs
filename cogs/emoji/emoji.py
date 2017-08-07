import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from typing import Union

class Emoji:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def emoji(self, ctx, emoji: str):
        """ Expand an emoji """
        print(emoji)
        await self.bot.say(emoji)


def setup(bot):
    n = Emoji(bot)
    bot.add_cog(n)

