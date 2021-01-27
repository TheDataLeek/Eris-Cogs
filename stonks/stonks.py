# stdlib
import random
import re
from pprint import pprint as pp
from io import BytesIO

# third party
import discord
from redbot.core import commands, bot

import yfinance as yf
import matplotlib.pyplot as plt

BaseCog = getattr(commands, "Cog", object)


class Stonks(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance


    @commands.command()
    async def stock(self, ctx, ticker: str):
        s = yf.Ticker(ticker)
        history = s.history()
        print(history.columns)
        s = s.info

        buf = BytesIO()

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        history[['Open']].plot(ax=ax)
        plt.savefig(buf, format='png')
        buf.seek(0)

        embed = discord.Embed(
            title=f"{s['longName']} ({ticker})",
            type='rich',
            description=f"Opened at {s['open']}"
        )
        img = discord.File(buf, filename=f"{ticker}.png")
        await ctx.send(embed=embed, file=img)

if __name__ == '__main__':
    # pp(yf.Ticker('GME').info)

    # history = yf.Ticker('GME').history()
    #
    # fig = plt.figure()
    # ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    # history[['Open']].plot(ax=ax)
    #
    # plt.show()
    # print(yf.Ticker('GME').history())

