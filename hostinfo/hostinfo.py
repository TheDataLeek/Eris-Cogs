import socket
import discord
from discord import utils
from redbot.core import commands, data_manager, Config, checks, Config
from redbot.core.utils import embed

from typing import List, Union, Optional

BaseCog = getattr(commands, "Cog", object)


class HostInfo(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot


    @commands.command()
    def hostinfo(self, ctx: commands.Context):
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)

        formatted = f"{hostname}@{ip_addr}"
        embedded_response = discord.Embed(
            title=f"Host Info",
            type="rich",
            description=formatted
        )
        embedded_response = embed.randomize_colour(embedded_response)

        await ctx.send(embed=embedded_response)

