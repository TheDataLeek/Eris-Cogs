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

BaseCog = getattr(commands, "Cog", object)


class Sarcasm(BaseCog):
    def __init__(self, bot):
        self.bot = bot

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

            ctx = await bot.get_context(message)

            # if random.random() <= 0.02:
            if str(ctx.author.id) == '142431859148718080' and random.random() <= 1:
                await ctx.send(add_sarcasm(clean_message))
                if random.random() <= 0.5:
                    with open('./data/sarcasm/img.png', 'rb') as fobj:
                        await ctx.send(file=discord.File(fobj))
                return

        self.bot.add_listener(sarcasm_module, 'on_message')

def add_sarcasm(message):
    return ''.join(c if random.random() <= 0.5 else c.upper() for c in message)
