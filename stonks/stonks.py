# stdlib
import random
import re
from pprint import pprint as pp

# third party
import discord
from redbot.core import commands, bot

import yfinance as yf
# import matplotlib.pyplot as plt

BaseCog = getattr(commands, "Cog", object)


class Stonks(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance


    @commands.command()
    async def stock(self, ctx, ticker: str):
        s = yf.Ticker(ticker).info

        embed = discord.Embed(
            title=f"{s['longName']} ({ticker})",
            type='rich',
            description=f"{s['open']}"
        )
        await ctx.send(embed=embed)


if __name__ == '__main__':
    pp(yf.Ticker('GME').info)
    # print(yf.Ticker('GME').history())

