import pathlib
import discord
from redbot.core import commands
from functools import reduce

BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        async def alot_of_patience(message):
            if message.guild is None:
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
                (bot.user.id == message.author.id or message.content.startswith("."))
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

            ctx = await bot.get_context(message)

            print(pathlib.Path().resolve())

            with open("./data/alot/alot.png", "rb") as fobj:
                await ctx.send(file=discord.File(fobj))
            return

        self.bot.add_listener(alot_of_patience, "on_message")
