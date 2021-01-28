# stdlib
import random
import re
from pprint import pprint as pp
from io import BytesIO
import hashlib
import string

# third party
import discord
from redbot.core import commands, bot

import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf

BaseCog = getattr(commands, "Cog", object)


class Stonks(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance


    @commands.command()
    async def stock(self, ctx, ticker: str, period=None, interval=None):
        """
        Request ticker info

        Periods = 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

        Intervals = 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        """
        ticker = ticker.upper()
        periods = [
            '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        ]
        if period not in periods:
            period = '1y'
        intervals = [
            '1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo'
        ]
        if interval not in intervals:
            interval = '1d'

        try:
            s = yf.Ticker(ticker)
            history = s.history(period=period, interval=interval)
            s = s.info
        except:
            await ctx.send(f'Something went wrong trying to find {ticker}!')
            return

        buf = BytesIO()
        mpf.plot(history, type='candle', mav=6, volume=True)
        plt.savefig(buf, format='png')
        buf.seek(0)

        marketCap = s.get('marketCap')
        try:
            marketCap = f"{marketCap:,}"
        except:
            marketCap = s.get('marketCap')

        fields = [
            f"Open: {s.get('open', '')} {s.get('currency', '')}",
            f"Previous Close: {s.get('previousClose', '')}",
            f"{s.get('dayLow', '')} <= yesterday <= {s.get('dayHigh', '')}",
            f"52wk Low: {s.get('fiftyTwoWeekLow', '')}",
            f"52wk High: {s.get('fiftyTwoWeekHigh', '')}",
            f"Market Cap: {marketCap}",
            f"Short Ratio: {s.get('shortRatio', '')}",
        ]

        color = hashlib.sha1(ticker.lower().encode('utf-8')).hexdigest()
        red = int(color[-6:-4], 16)
        green = int(color[-4:-2], 16)
        blue = int(color[-2:], 16)

        embed = discord.Embed(
            title=f"{s['longName']} ({ticker})",
            type='rich',
            description='\n'.join(fields),
            color=discord.Color.from_rgb(red, green, blue),
        )
        img = discord.File(buf, filename=f"{''.join(c for c in ticker.lower() if c in string.ascii_lowercase)}.png")
        await ctx.send(embed=embed, file=img)

if __name__ == '__main__':
    pp(yf.Ticker('GME').info)

    history = yf.Ticker('GME').history()

    mpf.plot(history, type='candle', mav=6, volume=True)

    plt.show()

    print(yf.Ticker('GME').history().columns)
