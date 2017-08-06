import discord
from discord.ext import commands
import random

async def message_events(message):
    await bot.say('its working')


def setup(bot):
    bot.add_listener(message_events, 'on_message')

