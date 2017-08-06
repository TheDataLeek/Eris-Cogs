import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from random import choice as randchoice
import aiohttp
import html
import json
import random

class Zalgo:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def zalgo(self, ctx, user : discord.Member=None):
        """Zalgo the text"""
        print(ctx)
        await self.bot.say('testing')


def setup(bot):
    n = Zalgo(bot)
    bot.add_cog(n)

