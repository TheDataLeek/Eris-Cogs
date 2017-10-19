#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
import sqlite3 as sq

import pathlib

WHOFILE = os.path.join(str(pathlib.Path.home()), 'whois.db')


class WhoIs:
    def __init__(self, bot):
        self.bot = bot

        con = sq.connect(WHOFILE)
        with con:
            con.execute(
                'CREATE TABLE IF NOT EXISTS usernames('
                    'userid TEXT,'
                    'name TEXT'
                ')'
            )

            con.execute(
                'CREATE TABLE IF NOT EXISTS usernicks('
                    'userid TEXT,'
                    'nick TEXT'
                ')'
            )

    @commands.command(pass_context=True, no_pm=True)
    async def whois(self, ctx, user: discord.Member=None):
        """
        Ask who a person is
        """
        if user is None:
            await self.bot.say('Please provide a user to specify')
            return

        con = sq.connect(WHOFILE)

        cursor = con.cursor()
        cursor.execute(
            'SELECT name FROM usernames WHERE userid=?',
            (user.id,)
        )
        names = cursor.fetchall()

        cursor.execute(
            'SELECT nick FROM usernicks WHERE userid=?',
            (user.id,)
        )
        nicks = cursor.fetchall()

        message = (
            'User: {}\n'
            'Realname: {}\n'
            'Known Aliases: {}'
        ).format(
            user.name,
            'No Name Known!' if len(names) == 0 else names[0][0],
            str(list(x[0] for x in nicks))
        )

        con.close()

        await self.bot.send_message(ctx.message.author, message)

    @commands.command(pass_context=True)
    async def theyare(self, ctx, user: discord.Member=None, realname: str=None):
        if user is None or realname is None:
            await self.bot.say('Please specify a <user> and a <realname>')
            return

        con = sq.connect(WHOFILE)
        cursor = con.cursor()

        con.execute(
            'SELECT * FROM usernames WHERE userid=?',
            (user.id,)
        )
        name_entry = cursor.fetchall()

        if len(name_entry) != 0:
            userid = name_entry[0][0]
            cursor.execute(
                'UPDATE usernames '
                    'SET name=? '
                    'WHERE userid=?',
                (realname, userid)
            )
            con.commit()
        else:
            cursor.execute(
                'INSERT INTO usernames('
                    'userid, name)'
                'VALUES(?,?)',
                (user.id, realname)
            )
            con.commit()
        con.close()

        await self.bot.say('User Registered')


def setup(bot):
    n = WhoIs(bot)
    bot.add_cog(n)


if __name__ == '__main__':
    WhoIs(None)
