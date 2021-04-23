# stdlib
from pprint import pprint as pp

# third party
import discord
from discord import utils
from redbot.core import commands, data_manager, Config, checks, Config

from typing import List, Union, Optional


BaseCog = getattr(commands, "Cog", object)


class HotelCalifornia(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot

        self.config = Config.get_conf(
            self,
            identifier=123458687089708978970987566,
            force_registration=True,
            cog_name="hotel_cali",
        )

        default_guild = {
            "member_role": None,
            "mod_role": None,
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    async def hotel(self, ctx):
        pass

    @hotel.command(pass_context=True)
    @checks.mod()
    async def memberrole(
        self, ctx: commands.Context, role: Optional[discord.Role] = None
    ):
        name = "None"
        str_id = None
        if role is not None:
            name = role.name
            str_id = str(role.id)

        await self.config.guild(ctx.guild).member_role.set(str_id)
        await ctx.send(f"Success, the member punishment role has been set to {name}")

    @hotel.command(pass_context=True)
    @checks.mod()
    async def modrole(self, ctx: commands.Context, role: Optional[discord.Role] = None):
        name = "None"
        str_id = None
        if role is not None:
            name = role.name
            str_id = str(role.id)

        await self.config.guild(ctx.guild).mod_role.set(str_id)
        await ctx.send(f"Success, the moderator punishment role has been set to {name}")

    @commands.command(pass_context=True)
    @checks.mod()
    async def punish(self, ctx: commands.Context, user: discord.Member):
        userroles: List[discord.Role] = user.roles
        ismod: bool = any(r.permissions.administrator for r in userroles)
        if ismod:
            role_id = await self.config.guild(ctx.guild).mod_role()
        else:
            role_id = await self.config.guild(ctx.guild).member_role()
        if role_id is None:
            await ctx.send("Error: Need to set member/moderator roles first!")
            return

        role = ctx.guild.get_role(int(role_id))
        if not user.bot:
            await user.add_roles(role)
            await ctx.send("Success - user punished")

    @commands.command(pass_context=True)
    @checks.mod()
    async def free(self, ctx: commands.Context, user: discord.Member):
        userroles: List[discord.Role] = user.roles
        ismod: bool = any(r.permissions.administrator for r in userroles)
        if ismod:
            role_id = await self.config.guild(ctx.guild).mod_role()
        else:
            role_id = await self.config.guild(ctx.guild).member_role()
        if role_id is None:
            await ctx.send("Error: Need to set member/moderator roles first!")
            return
        role = ctx.guild.get_role(int(role_id))
        if not user.bot:
            await user.remove_roles(role)
            await ctx.send("Success - user freed")
