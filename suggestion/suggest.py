# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager
from redbot.core.utils import embed
import aiohttp

from typing import Optional


BaseCog = getattr(commands, "Cog", object)


class Suggest(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def suggest(self, ctx, cog: Optional[str]=None):
        lines = [
            'Here\'s the repo for Eris Cogs: https://github.com/TheDataLeek/Eris-Cogs',
            "Want to submit a PR? Use this url! https://github.com/TheDataLeek/Eris-Cogs/compare",
            f"Here's the folder for the cog you've asked about! https://github.com/TheDataLeek/Eris-Cogs/tree/master/{cog}",
        ]
        embedded_response = discord.Embed(
            title=f"Contribute to Snek!",
            type="rich",
            description='\n'.join(lines),
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)
