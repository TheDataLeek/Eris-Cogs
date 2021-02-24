# stdlib
from pprint import pprint as pp

# third party
import discord
from discord import utils
from redbot.core import commands, data_manager, Config, checks


BaseCog = getattr(commands, "Cog", object)


class HotelCalifornia(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot
        
        self.signifier = 'ಠ'

    async def find_role(self, ctx: commands.Context):
        role: discord.Role = None
        for guild_role in ctx.guild.roles:
            if self.signifier in guild_role.name.lower():
                role = guild_role
                break
        else:
            await ctx.send("Sorry, I can't find that role!")

        return role

    @commands.command(pass_context=True)
    @checks.mod()
    async def punish(
        self, ctx: commands.Context, user: discord.Member
    ):
        role = await self.find_role(ctx)
        if not user.bot:
            await user.add_roles(role)

    @commands.command(pass_context=True)
    async def hotel_california(self, ctx: commands.Context):
        role = await self.find_role(ctx)
        msg: discord.Message = ctx.message
        user: discord.Member = msg.author

        user.add_roles(role)
