import io
from time import sleep
import discord
from redbot.core import commands, data_manager, Config, checks, bot
import random


BaseCog = getattr(commands, "Cog", object)


class Sarcasm(BaseCog):
    def __init__(self, bot_instance):
        self.bot: bot = bot_instance

        self.event_config = self.bot.get_cog('EventConfig')
        if self.event_config is None:
            raise FileNotFoundError('Need to install event_config')

        data_dir = data_manager.bundled_data_path(self)
        self.sarcastic_image = (data_dir / "img.png").read_bytes()

        self.bot.add_listener(self.add_sarcasm, "on_message")

    async def add_sarcasm(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        async with self.event_config.channel_lock(ctx):
            allowed: bool = await self.event_config.allowed(ctx, message)
            randomly_activated: bool = random.random() <= 0.02
            if not allowed or not randomly_activated:
                return

            new_message = self.add_sarcasm_to_string(message.clean_content)
            if new_message == message.clean_content:
                return

            async with ctx.typing():
                sleep(1)
                await ctx.send(new_message)
                if random.random() <= 0.1:
                    await ctx.send(file=discord.File(io.BytesIO(self.sarcastic_image), filename="sarcasm.png"))

    def add_sarcasm_to_string(self, message: str):
        return "".join(c if random.random() <= 0.5 else c.upper() for c in message)
