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
        self.prompts: Dict[str, List] = json.loads(
            (data_dir / "prompts.json").read_text()
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
        """
        Quote up to 6 users in a fun short story
        """
        message: discord.Message = ctx.message
        author: discord.Member = message.author

        num_members = max(1, len(users[:6]))  # set a floor and ceiling
        if not users:  # if empty
            users = [author]

        users = [
            (self.convert_realname(await self.get_realname(ctx, str(u.id))) or u.nick)
            for u in users
        ]
        random.shuffle(users)
        users = dict(zip(string.ascii_uppercase[:num_members], users))
        # await ctx.send(users)  # for debug
        # await ctx.send(num_members)
        prompts = self.prompts[f"prompts{int(num_members)}"]
        prompt = random.choice(prompts)
        await ctx.send(prompt.format(**users))

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
            # https://regex101.com/r/CrMmz9/1
            match = re.match(r'^(.{,32})[^a-z]', realname, re.IGNORECASE)
            if match is not None:
                realname = match.group(1)
                return realname
        else:
            return realname
