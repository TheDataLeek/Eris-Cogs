import io
import discord
from redbot.core import commands, data_manager, Config, checks, bot


BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

        self.event_config = self.bot.get_cog('EventConfig')
        if self.event_config is None:
            raise FileNotFoundError('Need to install event_config')

        data_dir = data_manager.bundled_data_path(self)
        self.alot = (data_dir / "ALOT.png").read_bytes()

        self.bot.add_listener(self.alot_event_handler, "on_message")

    async def alot_event_handler(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        allowed: bool = await self.event_config.allowed(ctx, message)
        keyword_in_message: bool = "alot" in message.clean_content.lower()
        if not allowed or not keyword_in_message:
            return

        await ctx.send(file=discord.File(io.BytesIO(self.alot), filename="alot.png"))

        await self.event_config.log_last_message(ctx, message)

