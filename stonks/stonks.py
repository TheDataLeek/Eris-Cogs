# stdlib
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

    @commands.command(aliases=["stonk"])
    async def stock(self, ctx, ticker: str, period=None, interval=None):
        """
        Request ticker info for given stock

        Periods = 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

        Intervals = 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        """
        ticker = ticker.upper()
        periods = [
            "1d",
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
            "10y",
            "ytd",
            "max",
        ]
        if period not in periods:
            period = "6mo"
        intervals = [
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ]
        if interval not in intervals:
            interval = "1d"

        try:
            s = yf.Ticker(ticker)
            history = s.history(period=period, interval=interval)
            s = s.info
            if len(history) == 0:
                raise Exception("Data not available for requested period/interval")
        except Exception as e:
            await ctx.send(f"Something went wrong trying to find {ticker}!\n```{e}```")
            return

        buf = plot_history(history)

        marketCap = s.get("marketCap")
        try:
            marketCap = f"{marketCap:,}"
        except:
            marketCap = s.get("marketCap")

        fields = [
            f"Open: {s.get('open', '')} {s.get('currency', '')}",
            f"Previous Close: {s.get('previousClose', '')}",
            f"{s.get('dayLow', '')} <= yesterday <= {s.get('dayHigh', '')}",
            f"52wk Low: {s.get('fiftyTwoWeekLow', '')}",
            f"52wk High: {s.get('fiftyTwoWeekHigh', '')}",
            f"Market Cap: {marketCap}",
            f"Short Ratio: {s.get('shortRatio', '')}",
        ]

        color = hashlib.sha1(ticker.lower().encode("utf-8")).hexdigest()
        red = int(color[-6:-4], 16)
        green = int(color[-4:-2], 16)
        blue = int(color[-2:], 16)

        embed = discord.Embed(
            title=f"{s['longName']} ({ticker})",
            type="rich",
            description="\n".join(fields),
            color=discord.Color.from_rgb(red, green, blue),
        )
        img = discord.File(
            buf,
            filename=f"{''.join(c for c in ticker.lower() if c in string.ascii_lowercase)}.png",
        )
        await ctx.send(embed=embed, file=img)


def plot_history(history):
    low = history.Low.min()
    high = history.High.max()
    fibline = lambda pct: low + ((high - low) * pct)

    style = mpf.make_mpf_style(base_mpf_style="charles", y_on_right=False)
    mpf.plot(
        history,
        type="candle",
        mav=6,
        volume=True,
        figsize=(8, 8),
        tight_layout=True,
        style=style,
        hlines={
            "hlines": [fibline(0.236), fibline(0.382), fibline(0.5), fibline(0.618)],
            "colors": "black",
            "linewidths": 0.5,
            "linestyle": "dashed",
        },
    )

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return buf


if __name__ == "__main__":
    history = yf.Ticker("GME").history(period="1d", interval="5m")
    print(history)
    buf = plot_history(history)
