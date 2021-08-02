import os
import discord
from redbot.core import commands, checks
import re
import requests
import sqlite3

import twilio
from twilio.rest import Client

import pathlib

BaseCog = getattr(commands, "Cog", object)

NUMBERFILE = os.path.join(str(pathlib.Path.home()), "numbers.txt")
WHOFILE = os.path.join(str(pathlib.Path.home()), "whois.db")

ZOEPHONE = os.environ.get("ZOEPHONE")
SNEKPHONE = os.environ.get("SNEKPHONE")


class Notify(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.client = Client()

        self.previous_message = None

        async def message_events(message):
            # Prevent acting on DM's
            if message.guild is None or message.guild.name.lower() != "cortex":
                return
            if (
                str(message.author.id) == "195663495189102593"
                and "announcements" in message.channel.name.lower()
            ):
                with open(NUMBERFILE, "r") as fobj:
                    current_numbers = [x for x in fobj.read().split("\n") if len(x) > 0]
                self.previous_message = message.clean_content
                message_to_send = "{}: {}".format(
                    get_realname(message.author.id) or message.author.display_name,
                    message.clean_content,
                )
                for number in current_numbers:
                    self.client.messages.create(
                        to=number, body=message_to_send, from_=SNEKPHONE
                    )
                await self.bot.send_message(
                    message.channel,
                    "[{}] have been notified.".format(", ".join(current_numbers)),
                )

        self.bot.add_listener(message_events, "on_message")

    @commands.group()
    async def notify(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @notify.command()
    @checks.is_owner()
    async def test(self, ctx):
        """
        Testing twilio integration, strictly for Zoe
        """
        if ZOEPHONE is not None:
            self.client.messages.create(
                to=ZOEPHONE, body="test message1", from_=SNEKPHONE
            )
            self.client.messages.create(
                to=ZOEPHONE, body="test message2", from_=SNEKPHONE
            )
            self.client.messages.create(
                to=ZOEPHONE, body="test message3", from_=SNEKPHONE
            )
            await ctx.send("Messages Sent Successfully")

    @notify.command()
    async def register(self, ctx, number: str):
        """Register a phone number for notifications"""
        if re.match("[0-9]+", number) and len(number) >= 9:
            with open(NUMBERFILE, "r") as fobj:
                current_numbers = [x for x in fobj.read().split("\n") if len(x) > 0]

            if number in current_numbers:
                await ctx.send("This number is already registered")
                return

            with open(NUMBERFILE, "a") as fobj:
                fobj.write(number)
                fobj.write("\n")
                await ctx.send("{} has been registered".format(number))
        else:
            await ctx.send("Please provide a valid phone number")

    @notify.command()
    async def delete(self, ctx, number: str):
        """delete a phone number for notifications"""
        if re.match("[0-9]+", number) and len(number) >= 10:
            with open(NUMBERFILE, "r") as fobj:
                current_numbers = [x for x in fobj.read().split("\n") if len(x) > 0]

            if number not in current_numbers:
                await ctx.send("This number is not registered")
                return

            current_numbers = list(set(current_numbers) - set([number]))
            with open(NUMBERFILE, "w") as fobj:
                for num in current_numbers:
                    fobj.write(num)
                    fobj.write("\n")
                await ctx.send("{} has been deleted".format(number))
        else:
            await ctx.send("Please provide a valid phone number")

    @notify.command()
    async def list(self, ctx):
        with open(NUMBERFILE, "r") as fobj:
            current_numbers = [x for x in fobj.read().split("\n") if len(x) > 0]
            await ctx.send(
                "The following numbers have been registered: [{}]".format(
                    ", ".join(current_numbers)
                )
            )
