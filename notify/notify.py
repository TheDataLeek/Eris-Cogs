import os
import discord
from redbot.core import commands
import re
import requests
import sqlite3

import twilio
from twilio.rest import Client

import pathlib

BaseCog = getattr(commands, "Cog", object)

NUMBERFILE = os.path.join(str(pathlib.Path.home()), 'numbers.txt')
WHOFILE = os.path.join(str(pathlib.Path.home()), 'whois.db')


def get_realname(userid: str):
    con = sqlite3.connect(WHOFILE)
    c = con.cursor()
    c.execute(
        'SELECT name '
        'FROM usernames '
        'WHERE userid=?',
        (userid,)
    )
    name = c.fetchall()
    con.close()
    if len(name) == 0:
        return None
    else:
        return name[0][0]


class Notify(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.client = Client()

        self.previous_message = None

        async def message_events(message):
            if '@\u200beveryone' in message.clean_content and 'police' in [x.name.lower() for x in message.author.roles]:
                with open(NUMBERFILE, 'r') as fobj:
                    current_numbers = [x for x in
                                       fobj.read().split('\n')
                                       if len(x) > 0]
                self.previous_message = message.clean_content
                message_to_send = '{}: {}'.format(get_realname(message.author.id) or message.author.display_name,
                                                  message.clean_content)
                for number in current_numbers:
                    self.client.messages.create(to=number, body=message_to_send, from_='4159410429')
                await self.bot.send_message(message.channel, '[{}] have been notified.'.format(', '.join(current_numbers)))

        self.bot.add_listener(message_events, 'on_message')

    @commands.group()
    async def notify(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @notify.command()
    async def test(self, ctx):
        self.client.messages.create(to='7192333514', body='test message1', from_='4159410429')
        self.client.messages.create(to='7192333514', body='test message2', from_='4159410429')
        self.client.messages.create(to='7192333514', body='test message3', from_='4159410429')
        await ctx.send('Messages Sent Successfully')

    @notify.command()
    async def register(self, ctx, number : str):
        """Register a phone number for notifications"""
        if re.match('[0-9]+', number) and len(number) >= 9:
            with open(NUMBERFILE, 'r') as fobj:
                current_numbers = [x for x in
                                   fobj.read().split('\n')
                                   if len(x) > 0]

            if number in current_numbers:
                await ctx.send('This number is already registered')
                return

            with open(NUMBERFILE, 'a') as fobj:
                fobj.write(number)
                fobj.write('\n')
                await ctx.send('{} has been registered'.format(number))
        else:
            await ctx.send('Please provide a valid phone number')

    @notify.command()
    async def delete(self, ctx, number : str):
        """delete a phone number for notifications"""
        if re.match('[0-9]+', number) and len(number) >= 10:
            with open(NUMBERFILE, 'r') as fobj:
                current_numbers = [x for x in
                                   fobj.read().split('\n')
                                   if len(x) > 0]

            if number not in current_numbers:
                await ctx.send('This number is not registered')
                return

            current_numbers = list(set(current_numbers) - set([number]))
            with open(NUMBERFILE, 'w') as fobj:
                for num in current_numbers:
                    fobj.write(num)
                    fobj.write('\n')
                await ctx.send('{} has been deleted'.format(number))
        else:
            await ctx.send('Please provide a valid phone number')

    @notify.command()
    async def list(self, ctx):
        with open(NUMBERFILE, 'r') as fobj:
            current_numbers = [x for x in
                               fobj.read().split('\n')
                               if len(x) > 0]
            await ctx.send('The following numbers have been registered: [{}]'.format(', '.join(current_numbers)))

