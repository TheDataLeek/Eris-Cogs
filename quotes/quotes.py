import discord
from redbot.core import commands, data_manager, Config
import random
import re
from functools import reduce
import string
import json
import pathlib
import string

from typing import Dict, List

BaseCog = getattr(commands, "Cog", object)


class Quotes(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        data_dir: pathlib.Path = data_manager.bundled_data_path(self)
        self.prompts: Dict[str, List] = (
            json.loads((data_dir / "prompts.json").read_text())
        )

        # need to also get whois
        self.config = Config.get_conf(
            self,
            identifier=746578326459283047523,
            force_registration=True,
            cog_name="whois",
        )

    @commands.command()
    async def quote(self, ctx: commands.Context, *users: discord.Member):
        message: discord.Message = ctx.message
        author: discord.Member = message.author

        num_members = max(1, len(users[:6]))   # set a floor and ceiling
        if not users:   # if empty
            users = [author]

        users = [
            (
                self.convert_realname(await self.get_realname(ctx, str(u.id)))
                or u.nick
            )
            for u in users
        ]
        users = dict(zip(string.ascii_uppercase[:num_members], users))
        await ctx.send(users)


    async def get_realname(self, ctx, userid: str):
        """
        Separate func here for others to use
        """
        async with self.config.guild(ctx.guild).whois_dict() as whois_dict:
            realname = whois_dict.get(userid, None)
        return realname

    def convert_realname(self, realname: str):
        if realname is None:
            return realname

        if len(realname) > 32:
            realname = realname.split(" ")[0]
            realname = "".join(
                c for c in realname if c.lower() in string.ascii_lowercase
            )
            return realname
        else:
            return realname
