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
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

    @commands.group()
    async def econf(self, ctx):
        pass

    @econf.command()
    @checks.mod()
    async def show(self, ctx):
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
                await ctx.send("Whitelist: " + ", ".join(whitelist))

            if len(blacklist) == 0:
                await ctx.send("Blacklist empty!")
            else:
                await ctx.send("Blacklist: " + ", ".join(blacklist))

    @econf.command()
    @checks.is_owner()
    async def toggle(self, ctx):
        new_status = not (await self.config.eris_events_enabled())
        await self.config.eris_events_enabled.set(new_status)
        await ctx.send(f"Done, we are now {'ON' if new_status else 'OFF'}")

    @econf.command()
    @checks.mod()
    async def reset(self, ctx):
        await self.config.guild(ctx.guild).channel_whitelist.set(["general"])
        await self.config.guild(ctx.guild).channel_blacklist.set([])
        await ctx.send("Done")

    @econf.command()
    @checks.mod()
    async def whitelist(self, ctx, channel: Union[str, discord.TextChannel] = None):
        await self.black_or_white_list(ctx, "whitelist", channel)

    @econf.command()
    @checks.mod()
    async def blacklist(self, ctx, channel: Union[str, discord.TextChannel] = None):
        await self.black_or_white_list(ctx, "blacklist", channel)

    async def black_or_white_list(
        self, ctx, which: str, channel: Union[str, discord.TextChannel]
    ):
        # todo -> check channel actually exists.....
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
        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        found = False
        for guild in guilds:
            actual_guild = await self.bot.fetch_guild(guild.id)
            for guild_channel in actual_guild.channels:
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
            if which == "whitelist":
                whitelist.append(channel)
                try:
                    blacklist.remove(channel)
                except ValueError:
                    pass
            else:
                blacklist.append(channel)
                try:
                    whitelist.remove(channel)
                except ValueError:
                    pass

        await ctx.send("Done")
