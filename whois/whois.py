import os
import discord
from redbot.core import commands
import sqlite3 as sq

import pathlib

BaseCog = getattr(commands, "Cog", object)

WHOFILE = os.path.join(str(pathlib.Path.home()), "whois.db")


class WhoIs(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        con = sq.connect(WHOFILE)
        with con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS usernames("
                "id INT PRIMARY KEY,"
                "userid TEXT,"
                "name TEXT"
                ")"
            )

            con.execute(
                "CREATE TABLE IF NOT EXISTS usernicks("
                "id INT PRIMARY KEY,"
                "userid TEXT,"
                "nick TEXT"
                ")"
            )

    @commands.command()
    async def iseveryone(self, ctx):
        con = sq.connect(WHOFILE)
        cursor = con.cursor()
        cursor.execute("SELECT userid, name " "FROM usernames")
        results = cursor.fetchall()
        results = [
            (ctx.guild.get_member(int(userid)), name) for userid, name in results
        ]

        CHAR_LIMIT = 2000
        characters = 0
        msg = ""
        for (mention, name) in results:
<<<<<<< HEAD
            if mention != "None":
=======
            if mention != "NONE":
>>>>>>> c5d57f748ff5d58ffde31615907aef7034f3a224
                to_append = "{} is {}\n".format(mention, name)
                characters += len(to_append)
                if characters >= CHAR_LIMIT:
                    await ctx.send(msg)
                    msg = ""
                    msg += to_append
                    characters = len(to_append)
                else:
                    msg += to_append
        if msg != "":
            await ctx.send(msg)
        con.close()

    @commands.command()
    async def iswho(self, ctx):
        name = " ".join(ctx.message.clean_content.split(" ")[1:]).lower()
        if name == "":
            await ctx.send("Please specify a person")
            return

        con = sq.connect(WHOFILE)

        cursor = con.cursor()

        cursor.execute(
            "SELECT userid " "FROM usernames " "WHERE name LIKE '%{}%'".format(name)
        )
        results = cursor.fetchall()
        if len(results) == 0:
            await ctx.send("No users found! Please try again.")
            return

        members = []
        for (userid,) in results:
            member = ctx.guild.get_member(int(userid))
            members.append(member.mention)
        await ctx.send("The following users match: {}".format(", ".join(members)))
        con.close()

    @commands.command(pass_context=True, no_pm=True)
    async def whois(self, ctx, user: discord.Member = None):
        """
        Ask who a person is
        """
        if user is None:
            await ctx.send("Please provide a user to specify")
            return

        con = sq.connect(WHOFILE)

        cursor = con.cursor()
        cursor.execute("SELECT name FROM usernames WHERE userid=?", (user.id,))
        names = cursor.fetchall()

        cursor.execute("SELECT nick FROM usernicks WHERE userid=?", (user.id,))
        nicks = cursor.fetchall()

        message = ("User: {}\n" "Realname: {}\n" "Known Aliases: {}").format(
            user.name,
            "No Name Known!" if len(names) == 0 else ", ".join(x[0] for x in names),
            str(list(x[0] for x in nicks)),
        )

        con.close()

        await ctx.send(message)

    @commands.command(pass_context=True)
    async def theyare(self, ctx, user: discord.Member = None, realname: str = None):
        if user is None or realname is None:
            await ctx.send("Please specify a <user> and a <realname>")
            return

        con = sq.connect(WHOFILE)
        cursor = con.cursor()

        cursor.execute("SELECT * FROM usernames WHERE userid=?", (user.id,))
        name_entry = cursor.fetchall()

        if len(name_entry) != 0:
            userid = name_entry[0][0]
            cursor.execute(
                "UPDATE usernames " "SET name=? " "WHERE userid=?", (realname, userid)
            )
            con.commit()
        else:
            cursor.execute(
                "INSERT INTO usernames(" "userid, name)" "VALUES(?,?)",
                (user.id, realname),
            )
            con.commit()
        con.close()

        await ctx.send("User Registered")
