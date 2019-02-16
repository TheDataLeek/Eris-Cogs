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
    points = Required(int, default=0)

db.bind(provider='sqlite', filename=str(db_file), create_db=True)
db.generate_mapping(create_tables=True)


@db_session
def get_user(uid):
    return User.select(lambda u: u.userID == uid).first()


class Battle(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def points(self, ctx, user: discord.Member=None):
        """
        List points that the user has
        """
        with db_session:
            if user is None:
                user = ctx.message.author

            db_user = get_user(user.id)

            if db_user is not None:
                await self.bot.say('User {} has {} points'.format(
                                    user.mention,
                                    db_user.points
                    ))
            else:
                User(userID=user.id)

    @commands.command(pass_context=True, no_pm=True)
    async def battle(self, ctx, user: discord.Member=None):
        """
        battles another user!
        """
        with db_session:
            author = get_user(ctx.message.author.id)
            member = get_user(user.id)

            if author.points <= 0:
                await self.bot.say('You have no points!')
                return
            if member.points <=0:
                await self.bot.say('They have no points!')
                return



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

        add_points = False
        if (userID not in POINT_TIMINGS) or (time.time() - POINT_TIMINGS[userID] > 60):
            POINT_TIMINGS[userID] = time.time()
            add_points = True

        user = get_user(userID)
        if user is None:
            user = User(userID=userID)

        if add_points:
            user.points += 1

    # We need to count each message
    async def count_reaction_add(reaction, _):
        # Prevent snek from voting on herself or counting
        if bot.user.id == reaction.message.author.id:
            return

        # Prevent acting on DM's
        if reaction.message.channel.name is None:
            return

        server          = reaction.message.channel.server.id
        channel         = reaction.message.channel.id
        userID          = reaction.message.author.id
        message_channel = reaction.message.channel.name.lower()

        user = get_user(userID)
        if user is None:
            user = User(userID=userID)

        if reaction.emoji == '👎':
            user.points -= 3
        elif reaction.emoji == '👍':
            user.points += 3

    # We need to count each message
    async def count_reaction_remove(reaction, _):
        # Prevent snek from voting on herself or counting
        if bot.user.id == reaction.message.author.id:
            return

        # Prevent acting on DM's
        if reaction.message.channel.name is None:
            return

        server          = reaction.message.channel.server.id
        channel         = reaction.message.channel.id
        userID          = reaction.message.author.id
        message_channel = reaction.message.channel.name.lower()

        user = get_user(userID)
        if user is None:
            user = User(userID=userID)

        if reaction.emoji == '👎':
            user.points += 3
        elif reaction.emoji == '👍':
            user.points -= 3

    bot.add_listener(count_message, 'on_message')
    bot.add_listener(count_reaction_add, 'on_reaction_add')
    bot.add_listener(parse_reaction_remove, 'on_reaction_remove')
