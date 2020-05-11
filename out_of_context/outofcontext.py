from time import sleep
import random
import re
import pathlib
import discord
from redbot.core import commands
from functools import reduce

BaseCog = getattr(commands, "Cog", object)


quotes = [
    _
    for _ in pathlib.Path("./data/events/ooc/ooc.txt").read_text().split("\n")
    if len(_) != 0
]


class OutOfContext(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.message_log = {}

        self.quote_hash = dict()
        for quote in quotes:
            quote_words = [_ for _ in quote.lower().split() if len(_) > 3]
            for word in quote_words:
                if word not in self.quote_hash:
                    self.quote_hash[word] = []

                self.quote_hash[word].append(quote)

        async def out_of_context_handler(message):
            # Prevent acting on DM's
            if message.guild is None or message.guild.name.lower() != 'cortex':
                return
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
            if "195663495189102593" == str(
                message.author.id
            ) or message.content.startswith("."):
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

            # channel-specific logs for last 5 messages
            chan_id = message.channel.id
            if chan_id not in self.message_log:
                self.message_log[chan_id] = [clean_message]
            else:
                self.message_log[chan_id].append(clean_message)
                if len(self.message_log[chan_id]) > 5:
                    self.message_log[chan_id].pop(0)

            ctx = await bot.get_context(message)

            if random.random() <= 0.99:  # 1% chance of activation
                return

            reply = self.get_quote(chan_id)

            async with ctx.typing():
                sleep(1)
                await message.channel.send(reply)

        self.bot.add_listener(out_of_context_handler, "on_message")

    @commands.command()
    async def penny(self, ctx):
        reply = self.get_quote(ctx.channel.id, most_recent=False)
        async with ctx.typing():
            sleep(1)
            await ctx.send(reply)

    def get_quote(self, channel_id, most_recent=True):
        reply = random.choice(quotes)
        if channel_id not in self.message_log:
            return reply  # just random if no logs

        split_msgs = [s.split(" ") for s in self.message_log[channel_id]]
        if most_recent:
            split_message = split_msgs[-1]  # just grab the last
        else:
            split_message = reduce(lambda a, b: a + b, split_msgs)
        random.shuffle(split_message)
        split_message = [s for s in split_message if len(s) > 3]

        for word in split_message:
            if word in self.quote_hash:
                reply = random.choice(self.quote_hash[word])
                break

        return reply
