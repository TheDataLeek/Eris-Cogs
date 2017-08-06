import discord
from discord.ext import commands
import random

def setup(bot):
    async def message_events(message):
        if 'zeb' in message.clean_content.lower():
            await bot.say(message.channel, 'I :heart: Zeb-kun')

    bot.add_listener(message_events, 'on_message')

