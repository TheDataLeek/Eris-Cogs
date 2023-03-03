# stdlib
from pprint import pprint as pp
import datetime as dt
import time

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

    @commands.command(pass_context=True)
    @checks.mod()
    async def mass_assign(self, ctx: commands.Context, base: discord.Role, new_role: discord.Role):
        """
        Mass assigns a role to users based on a current role.
        """
        for user in base.members:
            if not user.bot:
                await user.add_roles(new_role)

    @commands.command(pass_context=True)
    @checks.mod()
    async def mass_remove(self, ctx: commands.Context, base: discord.Role, new_role: discord.Role):
        """
        Mass assigns a role to users based on a current role.
        """
        for user in base.members:
            if not user.bot:
                await user.remove_roles(new_role)

    @commands.command(pass_context=True)
    @checks.mod()
    async def purge(self, ctx: commands.Context):
        """
        Mass removes roles from users if they haven't talked in too long
        """
        message: discord.Message
        guild: discord.Guild = ctx.guild
        channels: List[discord.TextChannel] = guild.text_channels

        userlog = {m.id: dt.datetime(1900, 1, 1) for m in guild.members}
        threshold: dt.datetime = dt.datetime.now() - dt.timedelta(days=365)

        stime = time.time()
        message_count = 0
        N = len(channels)

        for i, channel in enumerate(channels):
            await ctx.send(f"Searching 🔴{channel}🔴 for users to 💀PURGE💀 ({i / N:0.01%})")
            last_message_examined: discord.Message = None
            newer_than_a_year = True
            while newer_than_a_year:
                chunk = await channel.history(limit=2_000, before=last_message_examined).flatten()
                # if we run out of messages, stop
                if len(chunk) == 0:
                    break
                message_count += len(chunk)
                message: discord.Message

                for message in chunk:
                    userlog[message.author.id] = max(userlog.get(message.author.id, dt.datetime(1900, 1, 1)), message.created_at)
                    # if the messages are older than a year, stop
                    if message.created_at <= threshold:
                        newer_than_a_year = False
                        break

                last_message_examined = chunk[-1]

        delta = time.time() - stime
        minutes = delta // 60
        seconds = delta - (minutes * 60)

        users_to_purge = []
        for userid, last_message_dt in userlog.items():
            if last_message_dt <= threshold:
                users_to_purge.append(userid)

        users_to_purge = [
            guild.get_member(uid)
            for uid in users_to_purge
        ]

        message_to_send = (
            f"Done. Processed {message_count} messages, found {len(userlog)} users. \n"
            f"{len(users_to_purge)} must be 💀PURGED💀. \n"
            f"Duration of {minutes:0.0f} minutes, {seconds:0.03f} seconds."
        )
        await ctx.send(message_to_send)

        if users_to_purge:
            await ctx.send(', '.join([m.name for m in users_to_purge if m]))

        user: discord.Member
        for user in users_to_purge:
            if user:
                roles = user.roles
                await user.remove_roles(roles[1:])  # the first role is @everyone

        await ctx.send(f"Users 💀PURGED💀")


