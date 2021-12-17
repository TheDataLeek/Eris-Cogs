import discord
from redbot.core import commands, checks

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
    @checks.is_owner()
    async def isnt_december_the_best(self, ctx):
        for member in ctx.guild.members:
            await self.update_username(ctx, member, "Deer")

    @commands.command()
    @checks.is_owner()
    async def reset_deercember(self, ctx):
        for member in ctx.guild.members:
            await self.update_username(ctx, member, None)
