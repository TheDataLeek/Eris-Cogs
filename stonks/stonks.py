# stdlib
import random
import re

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
        s = yf.Ticker(ticker)
        await ctx.send(s.info)


