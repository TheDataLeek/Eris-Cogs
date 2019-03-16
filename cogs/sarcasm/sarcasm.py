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

        # DO NOT RESPOND TO SELF MESSAGES
        if bot.user.id == message.author.id or message.content.startswith('.'):
            return

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

        # IF DM's
        if message.channel.name is None:
            if random.random() < 0.1:
                realname = get_realname(message.author.id)
                if realname is None:
                    formatname = message.author.mention
                else:
                    formatname = realname
                new_message = random.choice(yandere)
                new_message = ' '.join(x.format(formatname)
                                       for x in new_message.split(' '))
                await bot.send_message(message.author, new_message)
            return

        message_channel = message.channel.name.lower()
        if reduce(
                lambda acc, n: acc or (n == message_channel),
                blacklist,
                False):
            return

        # first let's have a tiny chance of snek actually responding with ooc content
        if random.random() <= 0.02:
            await bot.send_message(message.channel, add_sarcasm(clean_message))
            return

    bot.add_listener(sarcasm_module, 'on_message')

