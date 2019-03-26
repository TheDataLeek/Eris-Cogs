import os
import time
import re
import discord
from discord.ext import commands
import random
from functools import reduce

import sqlite3
import pathlib
import csv


def add_sarcasm(message):
    return ''.join(c if random.random() <= 0.5 else c.upper() for c in message)


def setup(bot):
    async def sarcasm_module(message):
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

        if (
            # DO NOT RESPOND TO SELF MESSAGES
            (bot.user.id == message.author.id or message.content.startswith('.')) or
            (message.channel.name is None) or
            (reduce(
                lambda acc, n: acc or (n == message_channel),
                blacklist,
                False)) or
            ('@' in clean_message or 'thank' in clean_message)
            ):
            return

        if random.random() <= 0.02:
            await bot.send_message(message.channel, add_sarcasm(clean_message))
            return

    bot.add_listener(sarcasm_module, 'on_message')

