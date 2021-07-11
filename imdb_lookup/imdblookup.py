# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager
from redbot.core.utils import embed
import imdb


from typing import List


class MovieType(imdb.utils._Container):pass


BaseCog = getattr(commands, "Cog", object)


class IMDBLookup(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.ia = imdb.IMDb()

    @commands.group()
    async def imdb(self, ctx: commands.Context):
        pass

    @imdb.command()
    async def movie(self, ctx, *name: str):
        name = ' '.join(name)
        movies: List[imdb.Movie] = self.ia.search_movie(name)
        m: MovieType = movies[0]
        self.ia.update(m, info=['main', 'synopsis', 'plot'])

        embedded_response = discord.Embed(
            title=str(m),
            type="rich",
            description=(
                f"{m['plot'][0]}"
            )
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)

    @imdb.command()
    async def person(self, ctx, *name: str):
        name = ' '.join(name)
        people: List[imdb.Person] = self.ia.search_person(name)
