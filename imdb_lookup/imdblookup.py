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


class MovieType(imdb.utils._Container):
    pass


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
        name = " ".join(name)
        movies: List[imdb.Movie] = self.ia.search_movie(name)
        if not movies:
            await ctx.send("Unable to find movie!")
            return

        m: MovieType = movies[0]
        self.ia.update(
            m,
            info=["main", "summary", "plot", "cast", "rating", "runtime", "technical"],
        )

        summary = "\n".join(m.summary().split("\n")[2:])

        embedded_response = discord.Embed(
            title=f"Movie", type="rich", description=summary
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)

    @imdb.command()
    async def person(self, ctx, *name: str):
        name = " ".join(name)
        people: List[imdb.Person] = self.ia.search_person(name)


if __name__ == "__main__":
    name = "kong"
    ia = imdb.IMDb()
    movies = ia.search_movie(name)

    m = movies[0]
    ia.update(m, info=["main", "plot", "cast", "rating", "runtime", "technical"])

    print(m.summary())
    # return
    # cast = '\n'.join([str(p) for p in m['cast'][:10]])
    #
    # embedded_response = discord.Embed(
    #     title=f"{m} (User Rating: {m['rating']})",
    #     type="rich",
    #     # thumbnail=m['cover_url'][0],
    #     description=(
    #         f"Runtime: {m['runtime'][0]} minutes\n\n"
    #         f"*{m['plot'][0]}*\n\n"
    #         "__Cast__\n"
    #         f"{cast}\n..."
    #     )
    # )
    # await instance.movie(None, 'king kong')
    #
