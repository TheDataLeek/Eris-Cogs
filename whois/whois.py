import string
import sqlite3
import os
import discord
from redbot.core import commands, data_manager, Config, checks, bot
import sqlite3 as sq
import io
import pathlib


BaseCog = getattr(commands, "Cog", object)


class WhoIs(BaseCog):
    def __init__(self, bot_instance):
        self.bot: bot = bot_instance

        data_dir = data_manager.bundled_data_path(self)
        self.whois_file = data_dir / "whois.db"

        self.config = Config.get_conf(
            self,
            identifier=746578326459283047523,
            force_registration=True,
            cog_name="whois",
        )

        default_guild = {
            "whois_dict": {}
        }
        self.config.register_guild(**default_guild)

    @commands.command()
    @checks.is_owner()
    async def export_whois_db(self, ctx):
        con = sq.connect(str(self.whois_file))
        with con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS usernames("
                "userid INT PRIMARY KEY,"
                "name TEXT"
                ")"
            )

    @commands.command()
    async def theyare(self, ctx, user: discord.Member, *name: str):
        print(user.id)
        print(name)
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            whois_dict[user.id] = ' '.join(name)

        await ctx.send("Done")

    @commands.command()
    async def whois(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.message.author
        print(user.id)
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            print(user.id in whois_dict)
            print(whois_dict)
            realname = whois_dict.get(user.id, 'User not registered!')

        await ctx.send(realname)

    # @commands.command()
    # async def iseveryone(self, ctx):
    #     con = sq.connect(WHOFILE)
    #     cursor = con.cursor()
    #     cursor.execute("SELECT userid, name " "FROM usernames")
    #     results = cursor.fetchall()
    #     results = [
    #         (ctx.guild.get_member(int(userid)), name) for userid, name in results
    #     ]
    #     for (mention, name) in results:
    #         await ctx.send("{} is {}".format(mention, name))
    #     con.close()
    #
    # @commands.command()
    # async def iswho(self, ctx):
    #     name = " ".join(ctx.message.clean_content.split(" ")[1:]).lower()
    #     if name == "":
    #         await ctx.send("Please specify a person")
    #         return
    #
    #     con = sq.connect(WHOFILE)
    #
    #     cursor = con.cursor()
    #
    #     cursor.execute(
    #         "SELECT userid " "FROM usernames " "WHERE name LIKE '%{}%'".format(name)
    #     )
    #     results = cursor.fetchall()
    #     if len(results) == 0:
    #         await ctx.send("No users found! Please try again.")
    #         return
    #
    #     members = []
    #     for (userid,) in results:
    #         member = ctx.guild.get_member(int(userid))
    #         members.append(member.mention)
    #     await ctx.send("The following users match: {}".format(", ".join(members)))
    #     con.close()
    #
    # @commands.command(pass_context=True, no_pm=True)
    # async def whois_old(self, ctx, user: discord.Member = None):
    #     """
    #     Ask who a person is
    #     """
    #     if user is None:
    #         await ctx.send("Please provide a user to specify")
    #         return
    #
    #     con = sq.connect(WHOFILE)
    #
    #     cursor = con.cursor()
    #     cursor.execute("SELECT name FROM usernames WHERE userid=?", (user.id,))
    #     names = cursor.fetchall()
    #
    #     cursor.execute("SELECT nick FROM usernicks WHERE userid=?", (user.id,))
    #     nicks = cursor.fetchall()
    #
    #     message = ("User: {}\n" "Realname: {}\n").format(
    #         user.name,
    #         "No Name Known!" if len(names) == 0 else ", ".join(x[0] for x in names),
    #     )
    #
    #     con.close()
    #
    #     await ctx.send(message)
    #
    # @commands.command(pass_context=True)
    # async def theyare_old(self, ctx, user: discord.Member = None, *, realname: str = ""):
    #     if user is None or realname == "":
    #         await ctx.send("Please specify a <user> and a <realname>")
    #         return
    #
    #     con = sq.connect(WHOFILE)
    #     cursor = con.cursor()
    #
    #     cursor.execute("SELECT * FROM usernames WHERE userid=?", (user.id,))
    #     name_entry = cursor.fetchall()
    #
    #     if len(name_entry) != 0:
    #         userid = name_entry[0][0]
    #         cursor.execute(
    #             "UPDATE usernames " "SET name=? " "WHERE userid=?", (realname, userid)
    #         )
    #         con.commit()
    #     else:
    #         cursor.execute(
    #             "INSERT INTO usernames(" "userid, name)" "VALUES(?,?)",
    #             (user.id, realname),
    #         )
    #         con.commit()
    #     con.close()
    #
    #     await ctx.send("User Registered")

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.message.author
        await ctx.send(user.avatar_url)

    @commands.command()
    async def emoji(self, ctx, *args: discord.Emoji):
        for emoji in args:
            await ctx.send(emoji.url)

    def get_realname(self, userid: str):
        con = sqlite3.connect(WHOFILE)
        c = con.cursor()
        c.execute("SELECT name " "FROM usernames " "WHERE userid=?", (userid,))
        name = c.fetchall()
        con.close()
        if len(name) == 0:
            return None
        else:
            return name[0][0]

    def convert_realname(self, realname: str):
        if realname is None:
            return realname

        if len(realname) > 32:
            realname = realname.split(" ")[0]
            realname = "".join(c for c in realname if c.lower() in string.ascii_lowercase)
            return realname
        else:
            return realname
