import discord
from redbot.core import commands, checks
from typing import List

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

    @commands.command()
    @checks.mod()
    async def set_color(self, ctx: commands.Context, color: str):
        if color.startswith('#'):
            color = color[1:]

        if len(color) != 6:
            await ctx.send('Invalid Color!')
            return

        my_role: List[discord.Role] = [r for r in ctx.message.guild.roles if "snek color" == r.name.lower()]
        if len(my_role) != 1:
            await ctx.send("Error finding role, aborting!")
            return
        my_role: discord.Role = my_role[0]

        red = int(color[:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:], 16)

        color = discord.Color.from_rgb(red, green, blue)

        await my_role.edit(color=color)
