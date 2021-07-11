# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager
import imdb


from typing import List


BaseCog = getattr(commands, "Cog", object)


class IMDBLookup(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.ia = imdb.IMDb()

    @commands.group()
    def imdb(self):
        pass

    @commands.command()
    async def movie(self, ctx, *name: str):
        name = ' '.join(name)
        movies: List[imdb.Movie] = self.ia.search_movie(name, info='main')
        await ctx.send(movies[0])

    @commands.command()
    async def person(self, ctx, *name: str):
        name = ' '.join(name)
        people: List[imdb.Person] = self.ia.search_person(name, info='main')
