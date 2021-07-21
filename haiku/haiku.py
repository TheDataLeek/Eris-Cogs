import sys
import re

import discord
from redbot.core import commands, bot, Config
from redbot.core.utils import embed
import nltk
from nltk.corpus import cmudict
import syllables

from typing import List, Optional

nltk.download("cmudict")

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


class Haiku(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance

        self.syllable_dict = cmudict.dict()

        self.log = {}

        self.bot.add_listener(self.check_haiku, "on_message")

    def get_syllables(self, message: str) -> List:
        message_content, _ = re.subn(r"\s+", " ", message)
        message_content, _ = re.subn(
            r"[^a-z ]", "", message_content, flags=re.IGNORECASE
        )
        message_syllables = []
        split_message = [w for w in message_content.split(" ") if w]
        for word in split_message:
            cmu = self.syllable_dict.get(word.lower())
            if cmu is not None:
                if not isinstance(cmu[0], str):
                    cmu = cmu[0]
                syll_count = len([w for w in cmu if w[-1].isdigit()])
            else:
                syll_count = syllables.estimate(word)

            message_syllables.append((word, syll_count))

        return message_syllables

    async def check_haiku(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        # allowed: bool = await self.allowed(ctx, message)
        # if not allowed:
        #     return

        flag = True

        message_syllables = self.get_syllables(str(message.clean_content))

        # initial check
        total = sum([c for _, c in message_syllables])
        if total != 17:
            flag = False

        splits = []
        csum = 0
        cwords = []
        syll_flag = 1
        for word, count in message_syllables:
            csum += count
            cwords.append(word)
            ctotal = 5 if syll_flag else 7
            if csum == ctotal:
                splits.append(cwords)
                cwords = []
                csum = 0
                syll_flag ^= 1
            elif csum > ctotal:
                flag = False

        formatted = "\n".join(" ".join(w for w in s) for s in splits)
        self.log[ctx.message.id] = [message_syllables, total, formatted]

        if not flag:
            return

        embedded_response = discord.Embed(
            title=f"Accidental Haiku?",
            type="rich",
            description=formatted,
        )
        embedded_response = embed.randomize_colour(embedded_response)

        await ctx.send(embed=embedded_response)

    @commands.command()
    async def syllables(self, ctx, *msg: str):
        msg = " ".join(msg)
        syllables = self.get_syllables(msg)

        msg = [f"{word} ({count})" for word, count in syllables]
        msg = " ".join(msg)

        await ctx.send(msg)


    @commands.command()
    async def haikulog(self, ctx, msg_id: Optional[int] = None):
        message: discord.Message = ctx.message
        if message.reference:
            msg_id = message.reference.message_id

        if msg_id is None:
            return

        if msg_id in self.log:
            await ctx.send('\n'.join(str(_) for _ in self.log[msg_id]))


if __name__ == "__main__":
    import nltk
