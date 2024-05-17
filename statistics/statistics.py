import io
import discord
from redbot.core import commands, data_manager, Config, checks, bot

import polars as pl

BaseCog = getattr(commands, "Cog", object)


class Statistics(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.bot.add_listener(self.log_handler, "on_message")

    async def get_prefix(self, ctx: commands.Context) -> str:
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]
        return prefix

    async def log_handler(self, message: discord.Message):
        pass
