import discord
from redbot.core import commands, Config, checks
from typing import Union


BaseCog = getattr(commands, "Cog", object)


class EventConfig(BaseCog):
    def __init__(self, bot_instance):
        self.bot = bot_instance

        self.config = Config.get_conf(
            self,
            identifier=22222939019,
            force_registration=True,
            cog_name="event_config",
        )

        default_global = {
            "guild_list": [],
        }
        default_guild = {
            "channel_whitelist": ["general", "bot-chat"],
            "channel_blacklist": ["announcements", "news"],
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

    @commands.group()
    async def econf(self, ctx):
        pass

    @econf.command()
    @checks.is_owner()
    async def show(self, ctx):
        async with self.config.guild_list() as guild_list, self.config.guild(
            ctx.guild
        ).channel_whitelist() as whitelist, self.config.guild(
            ctx.guild
        ).channel_blacklist() as blacklist:
            if len(guild_list) == 0:
                await ctx.send("No servers have been registered!")
            else:
                await ctx.send("Servers: " + ", ".join(guild_list))

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
    async def add_server(self, ctx, *, server_name: str = ""):
        if server_name == "" and ctx.guild is not None:
            server_name = ctx.guild.name.lower()
        elif server_name == "" and ctx.guild is None:
            await ctx.send("Please provide a valid server name")
            return

        async with self.config.guild_list() as guild_list:
            guild_list.append(server_name)
            await ctx.send("Done")

    @econf.command()
    @checks.is_owner()
    async def remove_server(self, ctx, *, server_name: str = ""):
        if server_name == "" and ctx.guild is not None:
            server_name = ctx.guild.name.lower()
        elif server_name == "" and ctx.guild is None:
            await ctx.send("Please provide a valid server name")
            return

        async with self.config.guild_list() as guild_list:
            try:
                guild_list.remove(server_name)
                await ctx.send("Done")
            except ValueError:
                await ctx.send("Server was not in list!")

    @econf.command()
    @checks.mod()
    async def whitelist(self, ctx, channel: Union[str, discord.TextChannel]=None):
        await self.black_or_white_list(ctx, 'whitelist', channel)

    @econf.command()
    @checks.mod()
    async def blacklist(self, ctx, channel: Union[str, discord.TextChannel]=None):
        await self.black_or_white_list(ctx, 'blacklist', channel)

    async def black_or_white_list(self, ctx, which, channel):
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

        if which == 'whitelist':
            async with self.config.guild(ctx.guild).channel_whitelist() as whitelist:
                whitelist.append(channel)

            async with self.config.guild(ctx.guild).channel_blacklist() as blacklist:
                try:
                    blacklist.remove(channel)
                except ValueError:
                    pass
        else:
            async with self.config.guild(ctx.guild).channel_blacklist() as blacklist:
                blacklist.append(channel)

            async with self.config.guild(ctx.guild).channel_whitelist() as whitelist:
                try:
                    whitelist.remove(channel)
                except ValueError:
                    pass

        await ctx.send("Done")
