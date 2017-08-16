import os
import discord
from discord.ext import commands
import re

import twilio
from twilio.rest import Client

class Notify:
    def __init__(self, bot):
        self.bot = bot

        self.client = Client()

        self.previous_message = None

        async def message_events(message):
            if '@\u200beveryone' in message.clean_content and 'masters' in [x.name.lower() for x in message.author.roles]:
                with open('./data/notify/numbers.txt', 'r') as fobj:
                    current_numbers = [x for x in
                                       fobj.read().split('\n')
                                       if len(x) > 0]
                self.previous_message = message.clean_content
                message_to_send = '{}: {}'.format(message.author.display_name, message.clean_content)
                for number in current_numbers:
                    self.client.messages.create(to=number, body=message_to_send, from_='4159410429')
                await self.bot.send_message(message.channel, '[{}] have been notified.'.format(', '.join(current_numbers)))

        self.bot.add_listener(message_events, 'on_message')

    @commands.group(pass_context=True, no_pm=True)
    async def notify(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Please choose a command: `list`, `register`, or `delete`')

    @notify.command()
    async def test(self):
        self.client.messages.create(to='7192333514', body='test message1', from_='4159410429')
        self.client.messages.create(to='7192333514', body='test message2', from_='4159410429')
        self.client.messages.create(to='7192333514', body='test message3', from_='4159410429')

    @notify.command(pass_context=True)
    async def register(self, ctx, number : str):
        """Register a phone number for notifications"""
        if re.match('[0-9]+', number) and len(number) >= 9:
            with open('./data/notify/numbers.txt', 'r') as fobj:
                current_numbers = [x for x in
                                   fobj.read().split('\n')
                                   if len(x) > 0]

            if number in current_numbers:
                await self.bot.say('This number is already registered')
                return

            with open('./data/notify/numbers.txt', 'a') as fobj:
                fobj.write(number)
                fobj.write('\n')
                await self.bot.say('{} has been registered'.format(number))
        else:
            await self.bot.say('Please provide a valid phone number')

    @notify.command(pass_context=True)
    async def delete(self, ctx, number : str):
        """delete a phone number for notifications"""
        if re.match('[0-9]+', number) and len(number) >= 10:
            with open('./data/notify/numbers.txt', 'r') as fobj:
                current_numbers = [x for x in
                                   fobj.read().split('\n')
                                   if len(x) > 0]

            if number not in current_numbers:
                await self.bot.say('This number is not registered')
                return

            current_numbers = list(set(current_numbers) - set([number]))
            with open('./data/notify/numbers.txt', 'w') as fobj:
                for num in current_numbers:
                    fobj.write(num)
                    fobj.write('\n')
                await self.bot.say('{} has been deleted'.format(number))
        else:
            await self.bot.say('Please provide a valid phone number')

    @notify.command(pass_context=True)
    async def list(self, ctx):
        with open('./data/notify/numbers.txt', 'r') as fobj:
            current_numbers = [x for x in
                               fobj.read().split('\n')
                               if len(x) > 0]
            await self.bot.say('The following numbers have been registered: [{}]'.format(', '.join(current_numbers)))


def setup(bot):
    n = Notify(bot)
    bot.add_cog(n)
