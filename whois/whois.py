import string
import sqlite3
import os
import json
import discord
import io
import pathlib
import sqlite3
import re

from redbot.core import commands, data_manager, Config, checks, bot
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from typing import Union


BaseCog = getattr(commands, "Cog", object)


class WhoIs(BaseCog):
    def __init__(self, bot_instance):
        self.bot: bot = bot_instance


    @commands.command()
    async def iseveryone(self, ctx):
        con = sq.connect(WHOFILE)
        cursor = con.cursor()
        cursor.execute("SELECT userid, name " "FROM usernames")
        results = cursor.fetchall()
        results = [
            (ctx.guild.get_member(int(userid)), name) for userid, name in results
        ]

        max_character = 2000
        msg_size = 0
        msg = ""
        for (mention, name) in results:
            if mention is not "None":
                to_append = "{} is {}\n".format(mention, name)
                characters += len(to_append)
                if characters >= CHAR_LIMIT:
                    await ctx.send(msg)
                    msg = to_append
                    characters = len(to_append)
                else:
                    msg += to_append
        if msg is not "":
            await ctx.send(msg)
        con.close()
        data_dir = data_manager.bundled_data_path(self)


        self.config = Config.get_conf(
            self,
            identifier=746578326459283047523,
            force_registration=True,
            cog_name="whois",
        )

        default_guild = {"whois_dict": {}}
        self.config.register_guild(**default_guild)

    @commands.command()
    async def theyare(self, ctx, user: discord.Member, *name: str):
        """
        Set the real name of the user
        """
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            whois_dict[str(user.id)] = " ".join(name)

        await ctx.send("Done")

    @commands.command()
    async def whois(self, ctx, user: discord.Member = None):
        """
        Return the real name of the tagged user
        """
        if user is None:
            user = ctx.message.author
        realname = await self.get_realname(ctx, str(user.id))

        await ctx.send(realname or "User not registered!")

    async def get_realname(self, ctx, userid: str):
        """
        Separate func here for others to use
        """
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            realname = whois_dict.get(userid, None)
        return realname

    @commands.command()
    async def iswho(self, ctx, realname: str):
        """
        Reverse whois, where you search for the real name and get the tag of the matching users
        """
        member_ids_in_channel: list[str] = [
            str(member.id) for member in ctx.channel.members
        ]
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            matches = []
            for userid, name in whois_dict.items():
                if realname in name.lower() and str(userid) in member_ids_in_channel:
                    matches.append(ctx.guild.get_member(int(userid)).mention)

        if len(matches) == 0:
            await ctx.send("No users found!")
        else:
            await ctx.send(f"The following users match: {', '.join(matches)}")

    # @checks.mod()
    @commands.command()
    async def iseveryone(self, ctx):
        """
        Print all entries in the whois db
        """
        member_ids_in_channel: list[str] = [
            str(member.id) for member in ctx.channel.members
        ]
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            users = []
            for userid, name in whois_dict.items():
                if str(userid) not in member_ids_in_channel:
                    continue
                member: discord.Member = ctx.guild.get_member(int(userid))
                if member is not None:
                    users.append((member, name))
        users = sorted(users, key=lambda tup: tup[1])
        users = [
            f"{i}) **{member.display_name}** ({member.name}) is {name}"
            for i, (member, name) in enumerate(users)
        ]
        users = "\n".join(users)
        pages = list(pagify(users))
        await menu(ctx, pages, DEFAULT_CONTROLS)

    @commands.command()
    @checks.is_owner()
    async def import_whois(self, ctx):
        """
        Import whois db for guild from file
        """
        message: discord.Message = ctx.message
        file_to_import = None
        for attachment in message.attachments:
            if attachment.filename == "whois.json":
                file_to_import = attachment
                break
        if file_to_import is None:
            await ctx.send("Please provide a file attached to this command.")
            return

        try:
            new_whois_data = await file_to_import.read()
            new_whois_data = new_whois_data.decode("utf-8")
            new_whois_data = json.loads(new_whois_data)
        except:
            await ctx.send("Unable to parse input json!")
            return

        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            for userid, name in new_whois_data.items():
                whois_dict[userid] = name

        await ctx.send("Done")

    @commands.command()
    @checks.is_owner()
    async def export_whois(self, ctx):
        """
        Export whois db for guild from file
        """
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            output = json.dumps(whois_dict)
            await ctx.send(
                file=discord.File(io.StringIO(output), filename="whois.json")
            )

    def convert_realname(self, realname: str):
        if realname is None:
            return realname

        if len(realname) > 32:
            # https://regex101.com/r/CrMmz9/1
            match = re.match(r"^([a-z]{,32})[^a-z]", realname, re.IGNORECASE)
            if match is not None:
                realname = match.group(1)
                return realname
        else:
            return realname

    @commands.command(hidden=True)
    @checks.is_owner()
    async def import_from_legacy_db(self, ctx):
        """
        Import whois db for guild from legacy file
        """
        WHOFILE = os.path.join(str(pathlib.Path.home()), "whois.db")
        with sqlite3.connect(WHOFILE) as con:
            cursor = con.cursor()
            cursor.execute("SELECT userid, name FROM usernames")
            results = cursor.fetchall()

            async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
                for userid, name in results:
                    whois_dict[userid] = name

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """
        Show user avatar. Defaults to author if none specified
        """
        if user is None:
            user = ctx.message.author
        await ctx.send(user.avatar.url)

    @commands.command()
    async def display_avatar(self, ctx, user: discord.Member = None):
        """
        Show user avatar. Defaults to author if none specified
        """
        if user is None:
            user = ctx.message.author
        await ctx.send(user.display_avatar.url)

    @commands.command()
    async def emoji(self, ctx, *args: Union[discord.PartialEmoji, discord.Emoji]):
        """
        Show provided emoji. Must be a custom emoji, and the bot must have access to it.
        """
        for emoji in args:
            await ctx.send(emoji.url)
