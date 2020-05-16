import discord
from redbot.core import commands, checks

BaseCog = getattr(commands, "Cog", object)

class Clone(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.mod()
    async def clone(self, ctx, user: discord.Member):
        new_nick = user.display_name
        my_role = [r for r in user.guild.roles if "snek color" == r.name.lower()]
        if len(my_role) != 1:
            await ctx.send("Error finding role, aborting!")
            return
        my_role = my_role[0]
        avatar = await user.avatar_url_as(format="png", static_format="png").read()
        me = ctx.message.guild.me

        # await ctx.send(file=discord.File(avatar, filename='profile.png'))
        await me.edit(nick=new_nick)
        await self.bot.user.edit(avatar=avatar)
        await my_role.edit(color=user.color)
        await ctx.send("Done")