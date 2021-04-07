# stdlib
from pprint import pprint as pp

# third party
import discord
from discord import utils
from redbot.core import commands, data_manager, Config, checks

from typing import List


BaseCog = getattr(commands, "Cog", object)


class HotelCalifornia(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot

        self.signifier = "ಠ"
        self.mod_signifier = 'bad mod'

    async def find_role(self, ctx: commands.Context, ismod=False):
        role: discord.Role = None
        for guild_role in ctx.guild.roles:
            if ismod and self.mod_signifier in guild_role.name.lower():
                role = guild_role
                break
            elif self.signifier in guild_role.name.lower():
                role = guild_role
                break
        else:
            await ctx.send("Sorry, I can't find that role!")

        return role

    @commands.command(pass_context=True)
    @checks.mod()
    async def punish(self, ctx: commands.Context, user: discord.Member):
        userroles: List[discord.Role] = user.roles
        ismod: bool = any(r.permissions.administrator for r in userroles)
        role = await self.find_role(ctx, ismod=ismod)
        if not user.bot:
            await user.add_roles(role)

    @commands.command(pass_context=True)
    @checks.mod()
    async def free(self, ctx: commands.Context, user: discord.Member):
        userroles: List[discord.Role] = user.roles
        ismod: bool = any(r.permissions.administrator for r in userroles)
        role = await self.find_role(ctx, ismod=ismod)
        if not user.bot:
            await user.remove_roles(role)

    @commands.command(pass_context=True)
    async def hotel_california(self, ctx: commands.Context):
        await ctx.send("For Jeff <3")

        role = await self.find_role(ctx)
        msg: discord.Message = ctx.message
        user: discord.Member = msg.author

        await user.add_roles(role)
