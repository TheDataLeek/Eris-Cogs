import discord
from discord.ext import commands
import random

async def on_message(message):
    print(message)

def setup(bot):
    bot.add_listener(on_message)

