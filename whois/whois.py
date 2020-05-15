import string
import sqlite3
import os
import json
import discord
from redbot.core import commands, data_manager, Config, checks, bot
import io
import pathlib
import sqlite3


BaseCog = getattr(commands, "Cog", object)


class WhoIs(BaseCog):
    def __init__(self, bot_instance):
        self.bot: bot = bot_instance

        data_dir = data_manager.bundled_data_path(self)

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
    async def theyare(self, ctx, user: discord.Member, *name: str):
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            whois_dict[str(user.id)] = ' '.join(name)

        await ctx.send("Done")

    @commands.command()
    async def whois(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.message.author
        realname = self.get_realname(ctx, str(user.id)) or 'User not registered!'

        await ctx.send(realname)

    def get_realname(self, ctx, userid: str):
        """
        Separate func here for others to use
        """
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            realname = whois_dict.get(userid, None)
        return realname

    @commands.command()
    async def iswho(self, ctx, realname: str):
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            matches = []
            for userid, name in whois_dict:
                if realname in name.lower():
                    matches.append(ctx.guild.get_member(int(userid)).mention)

        if len(matches) == 0:
            await ctx.send("No users found!")
        else:
            await ctx.send(f"The following users match: {', '.join(matches)}")

    @commands.command()
    async def iseveryone(self, ctx):
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            for userid, name in whois_dict:
                member: discord.Member = ctx.guild.get_member(int(userid))
                await ctx.send(f"{member.nick} is {name}")

    @commands.command()
    @checks.is_owner()
    async def import_whois(self, ctx):
        message: discord.Message = ctx.message
        file_to_import = None
        for attachment in message.attachments:
            if attachment.filename == 'whois.json':
                file_to_import = attachment
                break
        if file_to_import is None:
            await ctx.send("Please provide a file attached to this command.")
            return

        try:
            new_whois_data = await file_to_import.read()
            new_whois_data = new_whois_data.decode('utf-8')
            new_whois_data = json.loads(new_whois_data)
        except:
            await ctx.send("Unable to parse input json!")
            return

        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            for userid, name in new_whois_data:
                whois_dict[userid] = name

    @commands.command()
    @checks.is_owner()
    async def export_whois(self, ctx):
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            output = json.dumps(whois_dict)
            await ctx.send(file=discord.File(io.StringIO(output), filename="whois.json"))

    def convert_realname(self, realname: str):
        if realname is None:
            return realname

        if len(realname) > 32:
            realname = realname.split(" ")[0]
            realname = "".join(c for c in realname if c.lower() in string.ascii_lowercase)
            return realname
        else:
            return realname

    @commands.command(hidden=True)
    @checks.is_owner()
    async def import_from_legacy_db(self, ctx):
        WHOFILE = os.path.join(str(pathlib.Path.home()), "whois.db")
        with sqlite3.connect(WHOFILE) as con:
            cursor = con.cursor()
            cursor.execute("SELECT userid, name " "FROM usernames")
            results = cursor.fetchall()

            async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
                for userid, name in results:
                    whois_dict[userid] = name

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
