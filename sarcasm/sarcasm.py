import io
from time import sleep
import discord
from redbot.core import commands, data_manager, Config, checks, bot
import random

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


class Sarcasm(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance):
        super().__init__()
        self.bot: bot = bot_instance

        data_dir = data_manager.bundled_data_path(self)
        self.sarcastic_image = (data_dir / "img.png").read_bytes()

        self.bot.add_listener(self.add_sarcasm, "on_message")

    async def add_sarcasm(self, message: discord.Message):
        randomly_activated: bool = random.random() <= 0.005
        if not randomly_activated:
            return

        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return

            new_message = self.add_sarcasm_to_string(message.clean_content)
            if new_message == message.clean_content:
                return

            async with ctx.typing():
                sleep(1)
                await ctx.send(new_message)
                if random.random() <= 0.1:
                    await ctx.send(
                        file=discord.File(
                            io.BytesIO(self.sarcastic_image), filename="sarcasm.png"
                        )
                    )

            await self.log_last_message(ctx, message)

    def add_sarcasm_to_string(self, message: str):
        return "".join(c if random.random() <= 0.5 else c.upper() for c in message)
