import io
import discord
from redbot.core import commands, data_manager, Config, checks, bot
from functools import reduce


BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

        self.event_config = Config.get_conf(
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
        self.event_config.register_global(**default_global)
        self.event_config.register_guild(**default_guild)

        data_dir = data_manager.bundled_data_path(self)
        self.alot = (data_dir / "ALOT.png").read_bytes()

        self.bot.add_listener(self.alot_of_patience, "on_message")

    async def alot_of_patience(self, message: discord.Message):
        server_list = await self.event_config.guild_list()
        if message.guild is None or message.guild.name.lower() not in server_list:
            return

        ctx = await self.bot.get_context(message)

        clean_message = message.clean_content.lower()

        message_channel = message.channel.name.lower()
        whitelisted_channels = await self.event_config.guild(ctx.guild).channel_whitelist()
        blacklisted_channels = await self.event_config.guild(ctx.guild).channel_blacklist()
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
