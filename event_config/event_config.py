import asyncio
import contextlib
import time
import discord
from redbot.core import commands, Config, checks, bot, utils
from typing import Union


BaseCog = getattr(commands, "Cog", object)


class EventConfig(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

        self.config = Config.get_conf(
            self,
            identifier=22222939019,
            force_registration=True,
            cog_name="event_config",
        )

        default_global = {
            "eris_events_enabled": True,
        }
        default_guild = {
            "channel_whitelist": ["general"],
            "channel_blacklist": [],
            "last_message_interacted_with_id": None,
            "enabled": False,
            "timeout": 0,
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

    @commands.group()
    async def econf(self, ctx):
        pass

    @econf.command()
    @checks.mod()
    async def timeout(self, ctx):
        now = time.time()
        timeout_ends = now + (60 * 60)  # one hour in seconds
        await self.config.guild(ctx.guild).timeout.set(timeout_ends)
        await ctx.send("Timed out for an hour!")

    @econf.command()
    @checks.mod()
    async def enable(self, ctx):
        await self.config.guild(ctx.guild).enabled.set(True)

    @econf.command()
    @checks.mod()
    async def disable(self, ctx):
        await self.config.guild(ctx.guild).enabled.set(False)

    @econf.command()
    @checks.mod()
    async def show(self, ctx):
        """
        Shows current status for global toggle and guild-specific white/blacklists.
        Permissions: >=Mod
        Usage: [p]econf show
        """
        events_status = await self.config.eris_events_enabled()
        guild_status = await self.config.guild(ctx.guild).enabled()
        async with self.config.guild(
            ctx.guild
        ).channel_whitelist() as whitelist, self.config.guild(
            ctx.guild
        ).channel_blacklist() as blacklist:
            if events_status:
                await ctx.send("Global events are currently ON")
            else:
                await ctx.send("Global events are currently OFF")

            if guild_status:
                await ctx.send("Guild events are currently ON")
            else:
                await ctx.send("Guild events are currently OFF")

            if len(whitelist) == 0:
                await ctx.send("Whitelist empty!")
            else:
                await ctx.send(f"Whitelist: {', '.join(whitelist)}")

            if len(blacklist) == 0:
                await ctx.send("Blacklist empty!")
            else:
                await ctx.send(f"Blacklist: {', '.join(blacklist)}")

    @econf.command()
    @checks.is_owner()
    async def toggle(self, ctx):
        """
        Toggles all event handlers on or off.
        Permissions: Owner
        Usage: [p]econf toggle
        """
        new_status = not (await self.config.eris_events_enabled())
        await self.config.eris_events_enabled.set(new_status)
        await ctx.send(f"Done, we are now {'ON' if new_status else 'OFF'}")

    @econf.command()
    @checks.mod()
    async def reset(self, ctx):
        """
        Resets guild white/blacklists to original settings.
        Permissions: >=Mod
        Usage: [p]econf reset
        """
        await self.config.guild(ctx.guild).channel_whitelist.set(["general"])
        await self.config.guild(ctx.guild).channel_blacklist.set([])
        await ctx.send("Done")

    @econf.command()
    @checks.mod()
    async def whitelist(self, ctx, channel: Union[str, discord.TextChannel] = None):
        """
        Adds a channel to the whitelist
        Permissions: >=Mod
        Usage: [p]econf whitelist <None|channel name|channel tag>
        """
        await self.black_or_white_list(ctx, "whitelist", channel)

    @econf.command()
    @checks.mod()
    async def blacklist(self, ctx, channel: Union[str, discord.TextChannel] = None):
        """
        Adds a channel to the blacklist
        Permissions: >=Mod
        Usage: [p]econf blacklist <None|channel name|channel tag>
        """
        await self.black_or_white_list(ctx, "blacklist", channel)

    async def black_or_white_list(
        self, ctx, which: str, channel: Union[str, discord.TextChannel]
    ):
        """
        goes through and actually handles the channel resolution + assertion + list management
        """
        if channel is None:
            channel = ctx.channel.name.lower()
        elif not isinstance(channel, str):
            if isinstance(channel, discord.TextChannel):
                channel = channel.name.lower()
            else:
                await ctx.send("Please provide a channel!")
                return
        else:
            channel = channel.lower()

        # check that the channel exists
        found = False
        for guild_channel in ctx.guild.channels:
            if guild_channel.name.lower() == channel:
                found = True

        if not found:
            await ctx.send("Channel not found!")
            return

        async with self.config.guild(
            ctx.guild
        ).channel_whitelist() as whitelist, self.config.guild(
            ctx.guild
        ).channel_blacklist() as blacklist:
            try:
                whitelist.remove(channel)
            except ValueError:
                pass

            try:
                blacklist.remove(channel)
            except ValueError:
                pass

            if which == "whitelist":
                whitelist.append(channel)
            else:
                blacklist.append(channel)

        await ctx.send("Done")
