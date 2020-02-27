import random
import re
import pathlib
import discord
from redbot.core import commands
from functools import reduce

BaseCog = getattr(commands, "Cog", object)


quotes = [_ for _ in pathlib.Path("./data/events/ooc/ooc.txt").read_text().split('\n') if len(_) != 0]


class OutOfContext(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.quote_hash = dict()
        for quote in quotes:
            quote_words = [_ for _ in quote.lower().split() if len(_) > 3]
            for word in quote_words:
                if word not in self.quote_hash:
                    self.quote_hash[word] = []

                self.quote_hash[word].append(quote)

        async def out_of_context_handler(message):
            clean_message = message.clean_content.lower()
            # MM: Added so list instead of string
            message_split = clean_message.split(" ")

            # BLACKLIST CHANNELS
            blacklist = [
                "news",
                "rpg",
                "the-tavern",
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

            regex = r"http|www"
            if re.search(regex, clean_message) is not None:
                return

            # DO NOT RESPOND TO SELF MESSAGES
            if "195663495189102593" == str(message.author.id) or message.content.startswith(
                    "."
            ):
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

            split_message = clean_message.split(' ')

            random.shuffle(split_message)

            if random.random() <= 0.01:
                for word in split_message:
                    if word in self.quote_hash:
                        await message.channel.send(random.choice(self.quote_hash[word]))
                        break
                else:
                    await message.channel.send(random.choice(quotes))

            return

        self.bot.add_listener(out_of_context_handler, "on_message")
