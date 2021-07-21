import sys

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

        self.bot.add_listener(self.no_sudo, "on_message")

    async def no_sudo(self, message: discord.Message):
        keyword_in_message: bool = "sudo" in message.clean_content.lower()
        if not keyword_in_message:
            return

        message_syllables = []
        for word in message.clean_content.split(' '):
            cmu = self.syllable_dict.get(word.lower())
            if cmu is not None:
                syll_count = len(cmu)
            else:
                syll_count = syllables.estimate(word)

            message_syllables.append((word, syll_count))

        # initial check
        total = sum([c for _, c in message_syllables])
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
                splits.append(cwords)
                cwords = []
                syll_flag ^= 1
            elif csum > ctotal:
                return

        ctx = await self.bot.get_context(message)
        await ctx.send('\n'.join(' '.join(w for w in s) for s in splits))

        # async with self.lock_config.channel(message.channel).get_lock():
        #     allowed: bool = await self.allowed(ctx, message)
        #     if not allowed:
        #         return
        #
        #     await self.log_last_message(ctx, message)



if __name__ == '__main__':
    import nltk