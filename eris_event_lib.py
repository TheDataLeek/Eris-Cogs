# stdlib
import time

# 3rd party
import discord
from redbot.core import Config, bot


class ErisEventMixin(object):
    def __init__(self):
        self.bot: bot = None
        self.config = Config.get_conf(
            None, identifier=22222939019, cog_name="event_config"
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

        self.lock_config = Config.get_conf(
            None, cog_name="ErisCogLocks", identifier=12340099888700
        )
        self.lock_config.register_channel(locked=None)  # This is never going to be set

    async def allowed(self, ctx, message: discord.Message):
        turned_on = (await self.config.eris_events_enabled()) and (
            await self.config.guild(ctx.guild).enabled()
        )

        if message.guild is None or not turned_on:
            return False

        message_channel = message.channel.name.lower()
        whitelisted_channels = await self.config.guild(ctx.guild).channel_whitelist()
        blacklisted_channels = await self.config.guild(ctx.guild).channel_blacklist()
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

        # check timeout
        now = time.time()
        timeout = await self.config.guild(ctx.guild).timeout()
        if timeout is None:
            timeout = 0
        if now <= timeout:
            return False

        last_message_interacted_with = await self.config.guild(
            ctx.guild
        ).last_message_interacted_with_id()
        # print(f"{last_message_interacted_with=}")
        # print(f"{message.id=}")
        if (
            last_message_interacted_with is not None
            and last_message_interacted_with == str(message.id)
        ):
            return False

        return True

    async def log_last_message(self, ctx, message: discord.Message):
        """
        prevents duplicate interactions by logging last message
        """
        await self.config.guild(ctx.guild).last_message_interacted_with_id.set(
            str(message.id)
        )
