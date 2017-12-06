#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
import discord.utils as disc_util
import sqlite3 as sq

import pathlib


RATINGSFILE = os.path.join(str(pathlib.Path.home()), 'bots.db')


def get_user_dbid(userid):
    con = sq.connect(RATINGSFILE)
    c = con.cursor()

    c.execute('SELECT id FROM ratings WHERE userid=?', (userid,))

    results = c.fetchall()

    userid = None

    if len(results) != 0:
        userid = results[0][0]

    con.close()
    return userid


def get_user_rating(userid):
    con = sq.connect(RATINGSFILE)
    c = con.cursor()

    c.execute('SELECT good, bad FROM ratings WHERE userid=?', (userid,))

    results = c.fetchall()

    rating = None

    if len(results) != 0:
        rating = results[0]

    con.close()
    return userid



class GoodBot:
    def __init__(self, bot):
        self.bot = bot

        con = sq.connect(RATINGSFILE)
        with con:
            con.execute(
                'CREATE TABLE IF NOT EXISTS ratings('
                    'id INT PRIMARY KEY,'
                    'userid TEXT,'
                    'good INT,'
                    'bad INT'
                ')'
            )

        self.previous_author = None

    @commands.command(pass_context=True, no_pm=True)
    async def rating(self, ctx, user: discord.Member=None):
        if user is None:
            await self.bot.say('Please actually provide a user you bot.')
            return
        if get_user_dbid(user.id) is None:
            await self.bot.say('{} hasn\'t been rated'.format(user.mention))
            return
        good, bad = get_user_rating(user.id)
        await self.bot.say('User {} has a score of {} ({}{}{})'.format(
                            user.mention,
                            good - bad,
                            good,
                            bad,
                            good + bad
            ))


def setup(bot):
    n = GoodBot(bot)
    bot.add_cog(n)

    async def goodbot(message):
        if ((bot.user.id == message.author.id) or (n.previous_author is None)):
            return

        clean_message = message.clean_content.lower()

        rating = None
        if 'good bot' in clean_message:
            rating = (1, 0)
        elif 'bad bot' in clean_message:
            rating = (0, 1)
        else:
            n.previous_author = message.author.id

        if rating is not None:
            con = sq.connect(RATINGSFILE)
            c = con.cursor()
            userid = get_user_dbid(message.author.id)
            if userid is None:
                c.execute('INSERT INTO ratings(userid, good, bad) VALUES(?,?,?)',
                          (message.author.id, *rating))
            else:
                old_rating = get_user_rating(message.author.id)
                good, bad = (old_rating[0] + rating[0],
                             old_rating[1] + rating[1])
                c.execute('UPDATE ratings SET good=?, bad=? WHERE id=?', (good, bad, userid))
            con.commit()
            con.close()

    bot.add_listener(goodbot, 'on_message')


if __name__ == '__main__':
    GoodBot(None)
