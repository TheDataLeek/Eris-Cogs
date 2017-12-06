#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
import discord.utils as disc_util
import sqlite3 as sq

import pathlib


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
        await self.bot.say('User {} has a score of {} ({}/{}/{})'.format(
                            user.mention,
                            good - bad,
                            good,
                            bad,
                            good + bad
            ))

    @commands.command(pass_context=True)
    async def botleaderboard(self, ctx):
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
        c.execute('SELECT userid, good, bad from ratings')
        results = c.fetchall()
        results = [(ctx.message.server.get_member(userid).mention,
                    good - bad,
                    good,
                    bad,
                    good + bad) for userid, good, bad in results]
        results.sort(key=lambda tup: -tup[1])
        results = [' - '.join([str(_) for _ in row]) for row in results]
        scores = '\n'.join(results)
        await self.bot.say('```Scores\n===========\n{}```'.format(scores))
        con.close()

    @commands.command(pass_context=True)
    async def see_previous(self, ctx):
        if ctx.message.author.id != '142431859148718080':
            return
        await self.bot.say(str(self.previous_author))


def setup(bot):
    n = GoodBot(bot)
    bot.add_cog(n)

    async def goodbot(message):
        if bot.user.id == message.author.id:
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
            con = sq.connect(RATINGSFILE)
            c = con.cursor()
            if not user_exists(n.previous_author[server][channel]):
                c.execute('INSERT INTO ratings(userid, good, bad) VALUES(?,?,?)',
                          (n.previous_author[server][channel], *rating))
                con.commit()
            else:
                oldgood, oldbad = get_user_rating(n.previous_author[server][channel], cursor=c)
                good, bad = (oldgood + rating[0],
                             oldbad + rating[1])
                c.execute('UPDATE ratings SET good=?, bad=? WHERE userid=?',
                          (good, bad, n.previous_author[server][channel]))
                con.commit()
            con.close()

    bot.add_listener(goodbot, 'on_message')


if __name__ == '__main__':
    GoodBot(None)
