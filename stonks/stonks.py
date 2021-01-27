# stdlib
import random
import re
from pprint import pprint as pp
from io import BytesIO
import hashlib

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
    async def stock(self, ctx, ticker: str, period=None):
        """
        Request ticker info

        Periods = 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        """
        periods = [
            '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        ]
        if period not in periods:
            period = '1y'
        s = yf.Ticker(ticker)
        history = s.history(period=period)
        print(history.columns)
        s = s.info

        buf = BytesIO()

        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        history[['Open']].plot(ax=ax)
        plt.savefig(buf, format='png')
        buf.seek(0)

        fields = [
            f"Open: {s['open']} {s['currency']}",
            f"Previous Close: {s['previousClose']}",
            f"{s['dayLow']} <= yesterday <= {s['dayHigh']}",
            f"52wk Low: {s['fiftyTwoWeekLow']}",
            f"52wk High: {s['fiftyTwoWeekHigh']}",
            f"Market Cap: {s['marketCap']:,}",
            f"Short Ratio: {s['shortRatio']}",
        ]

        color = hashlib.sha1(ticker.lower().encode('utf-8')).hexdigest()[-6:]

        embed = discord.Embed(
            title=f"{s['longName']} ({ticker})",
            type='rich',
            description='\n'.join(fields),
            color=color,
        )
        img = discord.File(buf, filename=f"{ticker}.png")
        await ctx.send(embed=embed, file=img)

if __name__ == '__main__':
    pp(yf.Ticker('GME').info)

    history = yf.Ticker('GME').history()

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    history[['Open']].plot(ax=ax)

    plt.show()

    print(yf.Ticker('GME').history().columns)
