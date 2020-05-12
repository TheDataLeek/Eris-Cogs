import io
import discord
from redbot.core import commands, data_manager
from functools import reduce


BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        data_dir = data_manager.bundled_data_path(self)
        self.alot = (data_dir / 'ALOT.png').read_bytes()
        self.bot.add_listener(self.alot_of_patience, "on_message")

    async def alot_of_patience(self, message):
        # Prevent acting on DM's
        if message.guild is None:  # or message.guild.name.lower() != "cortex":
            return

        clean_message = message.clean_content.lower()
        # MM: Added so list instead of string
        message_split = clean_message.split(" ")

        # BLACKLIST CHANNELS
        blacklist = [
            "news",
            "rpg",
            "events",
            "recommends",
            "politisophy",
            "eyebleach",
            "weeb-lyfe",
            "out-of-context",
            "jokes",
            "anime-club",
        ]

        message_channel = message.channel.name.lower()

        if "alot" not in clean_message:
            return

        if (
                # DO NOT RESPOND TO SELF MESSAGES
                (self.bot.user.id == message.author.id or message.content.startswith("."))
                or (message.channel.name is None)
                or (
                reduce(
                    lambda acc, n: acc or (n == message_channel), blacklist, False
                )
        )
                or ("thank" in clean_message)
                or ("http" in clean_message)
        ):
            return

        ctx = await self.bot.get_context(message)

        await ctx.send(file=discord.File(io.BytesIO(self.alot), filename='alot.png'))
