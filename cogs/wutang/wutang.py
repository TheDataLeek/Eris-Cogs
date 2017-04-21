import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from random import choice as randchoice
import aiohttp
import html
import random

class WuTang:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def enterthewu(self, ctx, user : discord.Member=None):
        """Gimme a name"""
        user = ctx.message.author
        await self.bot.say()


def setup(bot):
    n = WuTang(bot)
    bot.add_cog(n)

