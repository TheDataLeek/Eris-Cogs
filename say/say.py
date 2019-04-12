import discord
from redbot.core import commands, checks
from random import choice as randchoice

BaseCog = getattr(commands, "Cog", object)

GENERAL = 142435106257240064

class Say(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def say(self, ctx, what_to_say: str):
        """gimme a fact"""
        print(what_to_say)
        channel = self.bot.get_channel(GENERAL)
        print(channel)
        await channel.send(what_to_say)
        print('done')
