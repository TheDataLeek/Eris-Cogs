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
            await ctx.send("Sowwy, I'm unable to do this!")
            return

        if 2 > len(new_nick) > 32:
            await ctx.send("Sowwy, nicks must be between 2 and 32 characters!")
            return

    @commands.command(aliases=["bn"])
    async def isnt_december_the_best(self, ctx, user: discord.Member, *, new_nick: str = ""):
        for member in ctx.guild.members:
            await self.update_username(ctx, user, "Deer")
