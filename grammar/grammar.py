import os
import time
import re
import discord
from redbot.core import commands
import random
from functools import reduce
import io

import sqlite3
import pathlib
import csv

from spellchecker import SpellChecker

BaseCog = getattr(commands, "Cog", object)


class Grammar(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.spell = SpellChecker()

        async def grammar_module(message):
            if message.guild is None or int(message.guild.id) != 142435106257240064:
                return
            clean_message = message.clean_content.lower()
            # MM: Added so list instead of string
            message_split = clean_message.split(' ')

            # BLACKLIST CHANNELS
            blacklist = [
                'news',
                'rpg',
                'events',
                'recommends',
                'politisophy',
                'eyebleach',
                'weeb-lyfe',
                'out-of-context',
                'jokes',
                'anime-club',
            ]

            message_channel = message.channel.name.lower()

            if (message_channel != 'bot-chat') or (
                # DO NOT RESPOND TO SELF MESSAGES
                (bot.user.id == message.author.id or message.content.startswith('.')) or
                (message.channel.name is None) or
                (reduce(
                    lambda acc, n: acc or (n == message_channel),
                    blacklist,
                    False)) or
                ('@' in clean_message) or
                ('thank' in clean_message) or
                ('http' in clean_message)
                ):
                return

            # ctx = await bot.get_context(message)

            print(self.spell.unknown(message_split))
            # await ctx.send(lc.correct(clean_message, matches))

            return

        self.bot.add_listener(grammar_module, 'on_message')

