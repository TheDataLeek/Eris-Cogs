import discord
from discord.ext import commands
import random

async def message_events(message):
    print('personal func')
    print(message)

def setup(bot):
    print('starting setup')
    bot.add_listener(message_events, 'on_message')
    print('setup')

    print(bot.extra_events)

