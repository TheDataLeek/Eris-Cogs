import discord
from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)


class December(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    async def update_username(self, ctx, user, new_nick):
        try:
            await user.edit(nick=new_nick)
        except Exception as e:
            print(e)
            return

    @commands.command()
    async def isnt_december_the_best(self, ctx):
        for member in ctx.guild.members:
            await self.update_username(ctx, member, "Deer")
