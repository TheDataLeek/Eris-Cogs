#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
import discord.utils as disc_util
import sqlite3 as sq

import pprint as pp

import pathlib
import random
import time

from pony import orm

from pony.orm import Required, db_session

import pathlib

# we're gonna keep track of last point given in memory
POINT_TIMINGS = {}

"""
Let's start by defining our database
"""

db_file = pathlib.Path().home() / 'battle.db'

db = orm.Database()


class User(db.Entity):
    userID = Required(str)
    points = Required(int)


class Battle(object):
    def __init__(self, bot):
        self.bot = bot

        db.bind(provider='sqlite', filename=str(db_file), create_db=True)

    @commands.command(pass_context=True, no_pm=True)
    async def points(self, ctx, user: discord.Member=None):
        """
        Displays a user rating in the form <score> (<updoots>/<downdoots>/<totaldoots>)
        """
        if user is None:
            user = ctx.message.author

        userPoints = User[user.id].points

        await self.bot.say('User {} has {} points'.format(
                            user.mention,
                            userPoints
            ))


def setup(bot):
    # initialize instance of the battle
    n = Battle(bot)

    # Add the battle to the main bot instance
    bot.add_cog(n)

    # We need to count each message
    async def count_message(message, reaction=None, action=None):
        # Prevent snek from voting on herself or counting
        if bot.user.id == message.author.id:
            return

        # Prevent acting on DM's
        if message.channel.name is None:
            return

        server          = message.channel.server.id
        channel         = message.channel.id
        userID          = message.author.id
        message_channel = message.channel.name.lower()

        # don't do the #battle channel
        if 'battle' in message_channel:
            return

        if userID not in POINT_TIMINGS:
            POINT_TIMINGS[userID] = time.time()
            add_points_to_user(userID)
        elif time.time() - POINT_TIMINGS[userID] > 60:
            add_points_to_user(userID)

    bot.add_listener(count_message, 'on_message')


@db_session
def add_points_to_user(userID):
    user = User[userID]
    user.points += random.randint(1, 15)
    orm.commit()
