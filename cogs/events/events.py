import discord
from discord.ext import commands
import random

def setup(bot):
    async def message_events(message):
        # DO NOT RESPOND TO SELF MESSAGES
        if bot.user.id == message.author.id:
            return

        if 'zeb' in message.clean_content.lower():
            await bot.send_message(message.channel, 'Daisuki, Zeb-kun!')
            await bot.send_message(message.channel, ':eggplant: :eggplant: :sweat_drops: :sweat_drops:')

        print([x.name for x in message.author.roles])



    bot.add_listener(message_events, 'on_message')

