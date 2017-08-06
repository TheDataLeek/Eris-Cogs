import discord
from discord.ext import commands
import random

def setup(bot):
    async def message_events(message):
        await bot.say('its working')

    bot.add_listener(message_events, 'on_message')

