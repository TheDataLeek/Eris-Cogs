import os
from time import sleep
import random
import re
import pathlib
import discord
from redbot.core import commands, bot, checks
from functools import reduce

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


RETYPE = type(re.compile('a'))


# todo -> archive specified channel in db
# db format
# | message_id | contents |
# todo -> export
OOCFILE = pathlib.Path(os.path.join(str(pathlib.Path.home()), "ooc.txt"))
quotes = [
    _
    for _ in pathlib.Path(OOCFILE).read_text().split("\n")
    if len(_) != 0
]


class OutOfContext(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.message_match: RETYPE = re.compile('(?:([\"“])([^\"”]*?)(\"|”))', flags=re.IGNORECASE)   # flag not required

        self.message_log = {}

        self.quote_hash = dict()
        for quote in quotes:
            quote_words = [_ for _ in quote.lower().split() if len(_) > 3]
            for word in quote_words:
                if word not in self.quote_hash:
                    self.quote_hash[word] = []

                self.quote_hash[word].append(quote)

        self.bot.add_listener(self.out_of_context_handler, "on_message")

    async def out_of_context_handler(self, message):
        ctx = await self.bot.get_context(message)

        # channel-specific logs for last 5 messages
        chan_id = message.channel.id
        if chan_id not in self.message_log:
            self.message_log[chan_id] = [message.clean_content.lower()]
        else:
            self.message_log[chan_id].append(message.clean_content.lower())
            if len(self.message_log[chan_id]) > 5:
                self.message_log[chan_id].pop(0)

        async with self.lock_config.channel(message.channel).get_lock():
            if random.random() <= 0.99:  # 1% chance of activation
                return

            reply = self.get_quote(chan_id)
            async with ctx.typing():
                sleep(1)
                await message.channel.send(reply)

            await self.log_last_message(ctx, message)

    @commands.command()
    async def penny(self, ctx):
        """
        Penny for your thoughts? Posts a random out-of-context quote
        Usage: [p]penny
        """
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

    @commands.command()
    @checks.is_owner()
    async def update_ooc(self, ctx):
        channel: discord.TextChannel = ctx.channel

        ooc_list = []

        # let's start with just the latest 500
        message: discord.Message
        async for message in channel.history(limit=500):
            matches = self.message_match.findall(message.content)
            print(matches)

        print(ooc_list)
