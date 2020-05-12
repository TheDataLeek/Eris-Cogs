import io
import discord
from redbot.core import commands, data_manager, Config, checks, bot
from functools import reduce


BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

        self.config = Config.get_conf(
            self, identifier=928487392010, force_registration=True, cog_name="alot"
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

        data_dir = data_manager.bundled_data_path(self)
        self.alot = (data_dir / "ALOT.png").read_bytes()

        self.bot.add_listener(self.alot_of_patience, "on_message")

    @commands.group()
    async def alot(self, ctx):
        pass

    @alot.command()
    @checks.is_owner()
    async def servers(self, ctx):
        async with self.config.guild_list() as guild_list:
            if len(guild_list) == 0:
                await ctx.send("No servers have been registered!")
            else:
                await ctx.send("Servers: " + ", ".join(guild_list))

    @alot.command()
    @checks.is_owner()
    async def lists(self, ctx):
        async with self.config.guild(
            ctx.guild
        ).channel_whitelist() as whitelist, self.config.guild(
            ctx.guild
        ).channel_blacklist() as blacklist:
            if len(whitelist) == 0:
                await ctx.send("Whitelist empty!")
            else:
                await ctx.send("Whitelist: " + ", ".join(whitelist))

            if len(blacklist) == 0:
                await ctx.send("Blacklist empty!")
            else:
                await ctx.send("Blacklist: " + ", ".join(blacklist))

    @alot.command()
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

    @alot.command()
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

    @alot.command()
    @checks.mod()
    async def whitelist(self, ctx, channel=None):
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

        async with self.config.guild(ctx.guild).channel_whitelist() as whitelist:
            whitelist.append(channel)

        async with self.config.guild(ctx.guild).channel_blacklist() as blacklist:
            try:
                blacklist.remove(channel)
            except ValueError:
                pass

        await ctx.send("Done")

    @alot.command()
    @checks.mod()
    async def blacklist(self, ctx, channel=None):
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

        async with self.config.guild(ctx.guild).channel_blacklist() as blacklist:
            blacklist.append(channel)

        async with self.config.guild(ctx.guild).channel_whitelist() as whitelist:
            try:
                whitelist.remove(channel)
            except ValueError:
                pass

        await ctx.send("Done")

    async def alot_of_patience(self, message: discord.Message):
        server_list = await self.config.guild_list()
        if message.guild is None or message.guild.name.lower() not in server_list:
            return

        ctx = await self.bot.get_context(message)

        clean_message = message.clean_content.lower()

        message_channel = message.channel.name.lower()
        whitelisted_channels = await self.config.guild(ctx.guild).channel_whitelist()
        blacklisted_channels = await self.config.guild(ctx.guild).channel_blacklist()
        if (message_channel not in whitelisted_channels) or (
            message_channel in blacklisted_channels
        ):
            return

        if "alot" not in clean_message:
            return

        prefixes = await self.bot.get_valid_prefixes(guild=ctx.guild)
        if clean_message[0] in prefixes:
            return

        if (
            # DO NOT RESPOND TO SELF MESSAGES
            (self.bot.user.id == message.author.id)
            or ("http" in clean_message)
        ):
            return

        await ctx.send(file=discord.File(io.BytesIO(self.alot), filename="alot.png"))
