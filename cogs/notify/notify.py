import os
import discord
from discord.ext import commands
import random
from functools import reduce


def setup(bot):
    async def message_events(message):
        print(message.content)
        print(message.clean_content)
        if 'masters' in [x.name.lower() for x in message.author.roles] and '@everyone' in message.clean_content:
            await bot.send_message(message.channel, 'test')

    bot.add_listener(message_events, 'on_message')

