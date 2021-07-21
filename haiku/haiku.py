import sys
import re

import discord
from redbot.core import commands, bot, Config
import nltk
from nltk.corpus import cmudict
import syllables

nltk.download('cmudict')

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


class Haiku(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance

        self.syllable_dict = cmudict.dict()

        self.bot.add_listener(self.check_haiku, "on_message")

    async def check_haiku(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        allowed: bool = await self.allowed(ctx, message)
        if not allowed:
            return

        message_content, _ = re.subn(r"\s+", ' ', str(message.clean_content))
        message_content, _ = re.subn(r"[^a-z ]", '', message_content, flags=re.IGNORECASE)
        print(message_content)
        message_syllables = []
        split_message = [w for w in message_content.split(' ') if w]
        for word in split_message:
            cmu = self.syllable_dict.get(word.lower())
            if cmu is not None:
                if not isinstance(cmu[0], str):
                    cmu = cmu[0]
                syll_count = len([w for w in cmu if w[-1].isdigit()])
            else:
                syll_count = syllables.estimate(word)

            message_syllables.append((word, syll_count))
        print(message_syllables)

        # initial check
        total = sum([c for _, c in message_syllables])
        print(total)
        if total != 17:
            return

        splits = []
        csum = 0
        cwords = []
        syll_flag = 1
        for word, count in message_syllables:
            csum += count
            cwords.append(word)
            ctotal = (5 if syll_flag else 7)
            if csum == ctotal:
                print(cwords)
                splits.append(cwords)
                cwords = []
                csum = 0
                syll_flag ^= 1
            elif csum > ctotal:
                return

        print(splits)
        await ctx.send('\n'.join(' '.join(w for w in s) for s in splits))

        # async with self.lock_config.channel(message.channel).get_lock():
        #     allowed: bool = await self.allowed(ctx, message)
        #     if not allowed:
        #         return
        #
        #     await self.log_last_message(ctx, message)



if __name__ == '__main__':
    import nltk