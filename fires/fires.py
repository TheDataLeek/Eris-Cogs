# stdlib
import datetime as dt
import io

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class Fires(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.date_format = '%Y-%m-%d'
        self.url_string = "https://fsapps.nwcg.gov/data/lg_fire/lg_fire_nifc_{}.png"

    @commands.command()
    async def fires(self, ctx):
        """
        Show the firemap
        """
        date = dt.datetime.now()
        datestring = date.strftime(self.date_format)
        url = self.url_string.format(datestring)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img = await resp.read()
                await ctx.send(
                        file=discord.File(
                            img, filename=f"fires_{datestring}.png"
                            )
                        )
