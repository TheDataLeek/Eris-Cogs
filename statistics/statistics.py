import io
import discord
from redbot.core import commands, data_manager, Config, checks, bot

import polars as pl

BaseCog = getattr(commands, "Cog", object)


class Statistics(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        data_dir = data_manager.bundled_data_path(self)
        data_dir.mkdir(exist_ok=True, parents=True)
        self.logfile = data_dir / "events.log"

        self.logfile.open(mode="a")

        self.bot.add_listener(self.log_handler, "on_message")

    async def log_handler(self, message: discord.Message):
        pass
