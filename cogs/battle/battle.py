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

from pony.orm import Optional, Required, db_session

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

    strength = Optional(int)
    wisdom = Optional(int)
    dexterity = Optional(int)
    charisma = Optional(int)
    intelligence = Optional(int)
    constitution = Optional(int)

    hp = Optional(int)
    player_race = Optional(str)
    player_class = Optional(str)

    @property
    def st_mod(self): return int((self.strength - 10) / 2)

    @property
    def ws_mod(self): return int((self.wisdom - 10) / 2)

    @property
    def dx_mod(self): return int((self.dexterity - 10) / 2)

    @property
    def cr_mod(self): return int((self.charisma - 10) / 2)

    @property
    def in_mod(self): return int((self.intelligence - 10) / 2)

    @property
    def cn_mod(self): return int((self.constitution - 10) / 2)

    def generate_stat(self):
        rolls = sum(list(sorted(list(random.randint(1, 6) for _ in range(4))))[1:])
        return rolls

    @property
    def attack_roll(self):
        return random.randint(1, 20) + self.proficiency + self.dexterity

    @property
    def proficiency(self):
        breaks = [1, 5, 8, 12, 16, 21]
        level = self.level
        for i in range(len(breaks)):
            if breaks[i] <= level < breaks[i + 1]:
                return i + 2

    @property
    def level(self):
        breaks = [
            0,
            300,
            900,
            2_700,
            6_500,
            14_000,
            23_000,
            34_000,
            48_000,
            64_000,
            85_000,
            100_000,
            120_000,
            140_000,
            165_000,
            195_000,
            225_000,
            265_000,
            305_000,
            355_000,
        ]
        for i in range(len(breaks)):
            if breaks[i] <= self.points < breaks[i + 1]:
                return i + 1


db.bind(provider='sqlite', filename=str(db_file), create_db=True)
db.generate_mapping(create_tables=True)


@db_session
def get_user(uid):
    user = User.select(lambda u: u.userID == uid).first()
    if user is None:
        user = User(userID=uid)

    if user.strength is None:
        user.strength = user.generate_stat()
        user.charisma = user.generate_stat()
        user.wisdom = user.generate_stat()
        user.dexterity = user.generate_stat()
        user.constitution = user.generate_stat()
        user.intelligence = user.generate_stat()
        user.hp = random.randint(1, 6) * user.level

    return user


class Battle(object):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True, no_pm=True)
    async def status(self, ctx, user: discord.Member=None):
        """
        List status of user
        """
        with db_session:
            if user is None:
                user = ctx.message.author

            db_user = get_user(user.id)

            message = '\n'.join([
            'User {} has {} experience and is level {}',
            'Strength: {} ({})',
            'Intelligence: {} ({})',
            'Dexterity: {} ({})',
            'Wisdom: {} ({})',
            'Charisma: {} ({})',
            'Constitution: {} ({})',
            ])

            await self.bot.say(message.format(
                                user.mention,
                                db_user.points,
                                db_user.level,
                                db_user.strength,
                                db_user.st_mod,
                                db_user.intelligence,
                                db_user.in_mod,
                                db_user.dexterity,
                                db_user.dx_mod,
                                db_user.wisdom,
                                db_user.ws_mod,
                                db_user.charisma,
                                db_user.cr_mod,
                                db_user.constitution,
                                db_user.cn_mod,
                ))

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

        with db_session:
            user = get_user(userID)

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

        with db_session:
            user = get_user(userID)

            if reaction.emoji == '👎':
                user.points = max(0, user.points - 3)
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

        with db_session:
            user = get_user(userID)

            if reaction.emoji == '👎':
                user.points += 3
            elif reaction.emoji == '👍':
                user.points = max(0, user.points - 3)

    bot.add_listener(count_message, 'on_message')
    bot.add_listener(count_reaction_add, 'on_reaction_add')
    bot.add_listener(count_reaction_remove, 'on_reaction_remove')
