import contextlib
import time
import discord
from redbot.core import commands, Config, checks, bot
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
        }
        default_channel = {
            'is_locked': False
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        self.config.register_channel(**default_channel)

    @commands.group()
    async def econf(self, ctx):
        pass

    @econf.command()
    @checks.mod()
    async def show(self, ctx):
        """
        Shows current status for global toggle and guild-specific white/blacklists.
        Permissions: >=Mod
        Usage: [p]econf show
        """
        events_status = await self.config.eris_events_enabled()
        async with self.config.guild(
            ctx.guild
        ).channel_whitelist() as whitelist, self.config.guild(
            ctx.guild
        ).channel_blacklist() as blacklist:
            if events_status:
                await ctx.send("Events are currently ON")
            else:
                await ctx.send("Events are currently OFF")

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

    async def allowed(self, ctx, message: discord.Message):
        turned_on = await self.config.eris_events_enabled()
        if message.guild is None or not turned_on:
            return False

        message_channel = message.channel.name.lower()
        whitelisted_channels = await self.config.guild(
            ctx.guild
        ).channel_whitelist()
        blacklisted_channels = await self.config.guild(
            ctx.guild
        ).channel_blacklist()
        if (message_channel not in whitelisted_channels) or (
                message_channel in blacklisted_channels
        ):
            return False

        prefixes = await self.bot.get_valid_prefixes(guild=ctx.guild)
        if len(message.content) > 0 and message.content[0] in prefixes:
            return False

        if message.author.bot:
            return False

        if "http" in message.content:
            return False

        last_message_interacted_with = await self.config.guild(ctx.guild).last_message_interacted_with_id()
        print(f"{last_message_interacted_with=}")
        print(f"{message.id=}")
        if last_message_interacted_with is not None and last_message_interacted_with == str(message.id):
            return False

        return True

    async def log_last_message(self, ctx, message: discord.Message):
        """
        prevents duplicate interactions by logging last message
        """
        await self.config.guild(ctx.guild).last_message_interacted_with_id.set(str(message.id))

    @contextlib.asynccontextmanager
    async def channel_lock(self, ctx: commands.context):
        while True:
            is_locked = await self.config.channel(ctx.channel).is_locked()
            if not is_locked:
                break

            print(f"{ctx.channel.id} is locked!")
            time.sleep(0.5)

        try:
            await self.config.channel(ctx.channel).is_locked.set(True)
            yield self.config.channel(ctx.channel).is_locked()
        finally:
            await self.config.channel(ctx.channel).is_locked.set(False)
