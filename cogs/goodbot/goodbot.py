#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
import discord.utils as disc_util
import sqlite3 as sq

import pprint as pp

import pathlib
import random


RATINGSFILE = os.path.join(str(pathlib.Path.home()), 'bots.db')


def user_exists(userid, cursor=None):
    if cursor is None:
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
    else:
        c = cursor

    c.execute('SELECT * FROM ratings WHERE userid=?', (userid,))

    results = c.fetchall()

    exists = False

    if len(results) != 0:
        exists = True

    if cursor is None:
        con.close()

    return exists


def get_user_rating(userid, cursor=None):
    if cursor is None:
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
    else:
        c = cursor

    c.execute('SELECT good, bad FROM ratings WHERE userid=?', (userid,))

    results = c.fetchall()

    rating = None

    if len(results) != 0:
        rating = (results[0][0], results[0][1])
    else:
        # Add if doesn't exist, hopefully prevent crashes
        c.execute('INSERT INTO ratings(userid, good, bad) VALUES(?,?,?)',
                  (userid, 0, 0))
        con.commit()

    if cursor is None:
        con.close()

    return rating



class GoodBot:
    def __init__(self, bot):
        self.bot = bot

        con = sq.connect(RATINGSFILE)
        with con:
            con.execute(
                'CREATE TABLE IF NOT EXISTS ratings('
                    'id INT PRIMARY KEY,'
                    'userid TEXT UNIQUE,'
                    'good INT,'
                    'bad INT'
                ')'
            )
            con.commit()

        self.previous_author = dict()
        self.noticed = set()

    @commands.command(pass_context=True, no_pm=True)
    async def rating(self, ctx, user: discord.Member=None):
        """
        Displays a user rating in the form <score> (<updoots>/<downdoots>/<totaldoots>)
        """
        if user is None:
            await self.bot.say('Please actually provide a user you bot.')
            return
        if not user_exists(user.id):
            await self.bot.say('{} hasn\'t been rated'.format(user.mention))
            return
        good, bad = get_user_rating(user.id)
        await self.bot.say('User {} has a score of {}'.format(
                            user.mention,
                            good - bad
            ))

    @commands.command(pass_context=True)
    async def goodbots(self, ctx):
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
        c.execute('SELECT userid, good, bad from ratings')
        results = c.fetchall()
        results = []
        for userid, good, bad in results:
            try:
                results.append((ctx.message.server.get_member(userid).nick, good - bad))
            except Exception as e:
                print(e)
                pass
        results.sort(key=lambda tup: -tup[1])
        results = ['  '.join([str(_) for _ in row]) for row in results]
        scores = '\n'.join(results)
        await self.bot.say('```\nScores\n===========\n{}```'.format(scores))
        con.close()

    @commands.command(pass_context=True)
    async def see_previous(self, ctx):
        if ctx.message.author.id != '142431859148718080':
            return
        resolved_previous = {
            self.bot.get_server(server_id).name: {
                self.bot.get_channel(channel_id).name:
                    self.bot.get_server(server_id).get_member(user_id).name
                for channel_id, user_id
                in channels.items()
            }
            for server_id, channels
            in self.previous_author.items()
        }
        pretty_version = pp.pformat(resolved_previous)
        await self.bot.say('```{}```'.format(pretty_version))


def setup(bot):
    n = GoodBot(bot)
    bot.add_cog(n)

    async def goodbot(message, reaction=None, action=None):
        # Prevent snek from voting on herself or counting
        # if bot.user.id == message.author.id:
        #     return

        # Prevent acting on DM's
        if message.channel.name is None:
            return

        clean_message = message.clean_content.lower()
        server = message.channel.server.id
        channel = message.channel.id

        rating = None
        if 'good bot' in clean_message:
            rating = (1, 0)
        elif 'bad bot' in clean_message:
            rating = (0, 1)
        else:
            prev_author = message.author.id
            if server not in n.previous_author:
                n.previous_author[server] = dict()
            n.previous_author[server][channel] = prev_author

        if ((rating is not None) and
            (n.previous_author[server].get(channel) is not None) and
            (n.previous_author[server][channel] != message.author.id)):
            await rate_user(n.previous_author[server][channel], rating)

    async def rate_user(userid, rating):
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
        if not user_exists(userid):
            c.execute('INSERT INTO ratings(userid, good, bad) VALUES(?,?,?)',
                      (userid, *rating))
            con.commit()
        else:
            oldgood, oldbad = get_user_rating(userid, cursor=c)
            good, bad = (oldgood + rating[0],
                         oldbad + rating[1])
            # MM: You've had your fun
            # if ((userid == '142431859148718080') and ((good - bad) <= 0)):
            #     bad = good - 3
            c.execute('UPDATE ratings SET good=?, bad=? WHERE userid=?',
                      (good, bad, userid))
            con.commit()
        con.close()

    bot.add_listener(goodbot, 'on_message')

    async def parse_reaction_add(reaction, user):
        # Prevent acting on DM's
        if reaction.message.channel.name is None:
            return

        server = reaction.message.channel.server.id
        channel = reaction.message.channel.id

        rating = None   # (+, -)
        # MM: you've had your fun
        # Upvote SpatulaFish
        # if reaction.emoji in ['👎', '👍'] and reaction.message.author.id == '142431859148718080':
        #     rating = (1, 0)
        if reaction.emoji == '👎':
            # MM proposal:
            # Element of randomness: Self downvotes could result in updoot
            if user.id == reaction.message.author.id:
                if random.random() < 0.5:
                    rating = (1, 0)
                else:
                    rating = (0, 1)
            else:
                rating = (0, 1)
            # MM proposal:
            # Just call the poor sod a bad bot
            # if ((reaction.message.author.id != '142431859148718080') and (reaction.count >= 5)):
            #     await bot.delete_message(reaction.message)
            if ((reaction.count >= 5) and (reaction.message.id not in n.noticed)):
                await bot.send_message(reaction.message.channel,'{} IS A BAD BOT'.format(reaction.message.author.mention))
                n.noticed.add(reaction.message.id)
        elif reaction.emoji == '👍':
            # Downvote for self votes
            if user.id == reaction.message.author.id:
                rating = (0, 1)
            else:
                rating = (1, 0)
            if ((reaction.count >= 5) and (reaction.message.id not in n.noticed)):
                await bot.send_message(reaction.message.channel,
                                       '{} IS A GOOD BOT'.format(reaction.message.author.mention))
                n.noticed.add(reaction.message.id)

        if rating is not None:
            await rate_user(reaction.message.author.id, rating)

    async def parse_reaction_remove(reaction, user):
        # Prevent acting on DM's
        if reaction.message.channel.name is None:
            return

        server = reaction.message.channel.server.id
        channel = reaction.message.channel.id

        rating = None
        # do nothing for remove, already punished once for self votes
        if user.id == reaction.message.author.id:
            return
        elif reaction.emoji == '👎':
            rating = (1, 0)
        elif reaction.emoji == '👍':
            rating = (0, 1)

        await rate_user(reaction.message.author.id, rating)

    bot.add_listener(parse_reaction_add, 'on_reaction_add')
    bot.add_listener(parse_reaction_remove, 'on_reaction_remove')
