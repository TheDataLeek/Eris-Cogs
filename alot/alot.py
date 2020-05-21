import io
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin


BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        data_dir = data_manager.bundled_data_path(self)
        self.alot = (data_dir / "ALOT.png").read_bytes()

        self.bot.add_listener(self.alot_event_handler, "on_message")

    async def alot_event_handler(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            keyword_in_message: bool = "alot" in message.clean_content.lower()
            if not allowed or not keyword_in_message:
                return

            await ctx.send(
                file=discord.File(io.BytesIO(self.alot), filename="alot.png")
            )

            await self.log_last_message(ctx, message)
