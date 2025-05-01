# stdlib
from random import choice as randchoice
import pathlib
from typing import List

# 3rd party
import discord
from redbot.core import commands, data_manager


BaseCog = getattr(commands, "Cog", object)


## TODO -> Docstrings


class Fact(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        data_dir: pathlib.Path = data_manager.bundled_data_path(self)
        self.bearfacts: List[str] = (
            (data_dir / "bearfacts.txt").read_text(encoding="utf-8").split("\n")
        )
        self.snekfacts: List[str] = (
            (data_dir / "snekfacts.txt").read_text(encoding="utf-8").split("\n")
        )

    @commands.group()
    async def fact(self, ctx):
        """
        todo -> specify subcommands
        """
        pass

    @fact.command()
    async def random(self, ctx):
        await ctx.send(randchoice(randchoice([self.bearfacts, self.snekfacts])))

    @fact.command()
    async def snek(self, ctx):
        await ctx.send(randchoice(self.snekfacts))

    @fact.command()
    async def bear(self, ctx):
        await ctx.send(randchoice(self.bearfacts))
