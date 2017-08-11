import os
import discord
from discord.ext import commands
import re

import twilio
from twilio.rest import Client

class Notify:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def notify(self, ctx):
        pass

    @notify.command(pass_context=True, name='register')
    async def _register(self, ctx, number : str):
        """Register a phone number for notifications"""
        if re.match('[0-9]+', number) and len(str) >= 10:
            with open('./data/notify/numbers.txt', 'r') as fobj:
                current_numbers = [x for x in
                                   fobj.readlines()
                                   if len(x) > 0]

            if number in current_numbers:
                await self.bot.say('This number is already registered')
                return

            with open('./data/notify/numbers.txt', 'a') as fobj:
                fobj.write(number)
                fobj.write('\n')
        else:
            await self.bot.say('Please provide a valid phone number')

    @notify.command(pass_context=True, name='delete')
    async def _delete(self, ctx, number : str):
        """delete a phone number for notifications"""
        if re.match('[0-9]+', number) and len(str) >= 10:
            with open('./data/notify/numbers.txt', 'r') as fobj:
                current_numbers = [x for x in
                                   fobj.read().split('\n')
                                   if len(x) > 0]

            if number not in current_numbers:
                await self.bot.say('This number is not registered')
                return

            with open('./data/notify/numbers.txt', 'w') as fobj:
                for num in current_numbers:
                    fobj.write(num)
                    fobj.write('\n')
                await self.bot.say('{} has been deleted'.format(number))
        else:
            await self.bot.say('Please provide a valid phone number')

    @notify.command(pass_context=True, name='list')
    async def _list(self, ctx):
        with open('./data/notify/numbers.txt', 'r') as fobj:
            current_numbers = [x for x in
                               fobj.read().split('\n')
                               if len(x) > 0]
            await self.bot.say('The following numbers have been registered: [{}]'.format(', '.join(current_numbers)))


def setup(bot):
    n = Notify(bot)
    bot.add_cog(n)

    client = Client()

    async def message_events(message):
        if '@everyone' in message.clean_content and 'masters' in [x.name.lower() for x in message.author.roles]:
            await bot.send_message(message.channel, 'test')

    bot.add_listener(message_events, 'on_message')
