import os
import io
from time import sleep
import random
import re
import pathlib
import discord
from redbot.core import commands, bot, checks, data_manager, Config
from functools import reduce

from typing import List, Optional

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


RETYPE = type(re.compile("a"))


class OutOfContext(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.config = Config.get_conf(
            self,
            identifier=875239875438276234987523048752087,
            force_registration=True,
            cog_name="ooc",
        )

        default_guild = {
            "ooc_blocklist": [],
            "quotes": [],
            "quote_hash": [],
        }
        self.config.register_guild(**default_guild)

        self.message_match: RETYPE = re.compile(
            '(?:(["“])([^"”]*?)("|”))', flags=re.IGNORECASE
        )  # flag not required

        self.message_log = {}

        self.bot.add_listener(self.out_of_context_handler, "on_message")

    @commands.group()
    async def ooc(self, ctx: commands.Context):
        pass

    @ooc.command()
    @checks.mod()
    async def block(self, ctx: commands.Context, *phrase):
        """
        Add phrase to blocklist
        """
        phrase = " ".join(phrase).lower()
        async with self.config.guild(ctx.guild).ooc_blocklist() as blocklist:
            blocklist.append(phrase)
        await ctx.send("Success")

    @ooc.command()
    @checks.mod()
    async def show(self, ctx: commands.Context):
        """
        Show current blocklist. This will eventually break if you have too many lines.
        """
        lines = []
        async with self.config.guild(ctx.guild).ooc_blocklist() as blocklist:
            for i, phrase in enumerate(blocklist):
                lines.append(f"{i}  {phrase}")
        lines = "\n".join(lines)
        await ctx.send(f"```\n{lines}\n```")

    @ooc.command()
    @checks.mod()
    async def remove(self, ctx: commands.Context, index: int):
        """
        Remove item from current blocklist.
        """
        async with self.config.guild(ctx.guild).ooc_blocklist() as blocklist:
            if 0 <= index < len(blocklist):
                blocklist.pop(index)
        await ctx.send("Success")

    @ooc.command()
    @checks.mod()
    async def download(self, ctx: commands.Context):
        """
        Remove item from current blocklist.
        """
        async with self.config.guild(ctx.guild).quotes() as quotes:
            await ctx.send(
                file=discord.File(
                    io.StringIO('\n'.join(quotes)), filename="ooc.txt"
                )
            )

    async def out_of_context_handler(self, message):
        if random.random() <= 0.99:  # 1% chance of activation
            return

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
            allowed: bool = await self.allowed(ctx, message)
            if not allowed:
                return

            reply = self.get_quote(ctx)
            async with ctx.typing():
                sleep(1)
                await message.channel.send(reply)

            await self.log_last_message(ctx, message)

    @commands.command()
    async def penny(self, ctx: commands.Context):
        """
        Penny for your thoughts? Posts a random out-of-context quote
        Usage: [p]penny
        """
        reply = self.get_quote(ctx, most_recent=False)
        async with ctx.typing():
            sleep(1)
            await ctx.send(reply)

    async def get_quote(self, ctx: commands.Context, most_recent: Optional[bool]=True):
        channel_id: int = ctx.channel.id

        async with self.config.guild(ctx.guild).quotes() as quotes:
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

        async with self.config.guild(ctx.guild).quote_hash() as quote_hash:
            for word in split_message:
                if word in quote_hash:
                    reply = random.choice(quote_hash[word])
                    break

        return reply

    @ooc.command()
    @checks.mod()
    async def update(self, ctx: commands.Context):
        """
        Updates the out of context quotes from the current channel. WILL OVERWRITE ALL OTHERS!
        Usage: [p]update_ooc
        """
        channel: discord.TextChannel = ctx.channel

        async with self.config.guild(ctx.guild).ooc_blocklist() as blocklist:
            phrases_to_block = blocklist

        ooc_list = []

        # let's start with just the latest 500
        message: discord.Message
        last_message_examined: discord.Message = None
        message_count = 0
        while True:
            chunk = await channel.history(
                limit=500, before=last_message_examined
            ).flatten()
            if len(chunk) == 0:
                break
            message_count += len(chunk)
            for message in chunk:
                matches: List[tuple] = self.message_match.findall(message.content)
                for match in matches:
                    quote = match[1]
                    if quote == "":
                        continue

                    for phrase in phrases_to_block:
                        if phrase in quote.lower():
                            break
                    else:
                        ooc_list.append(quote)

            last_message_examined = message

        ooc_list = list(set(ooc_list))

        await self.config.guild(ctx.guild).quotes.set(ooc_list)

        quote_hash = dict()
        for quote in ooc_list:
            quote_words = [_ for _ in quote.lower().split() if len(_) > 3]
            for word in quote_words:
                if word not in self.quote_hash:
                    quote_hash[word] = []

                quote_hash[word].append(quote)

        await self.config.guild(ctx.guild).quote_hash.set(quote_hash)

        await ctx.send(
            f"Done. Processed {message_count} messages, found {len(ooc_list)} quotes."
        )
