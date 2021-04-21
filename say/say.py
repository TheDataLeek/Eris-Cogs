import discord
from redbot.core import commands, checks, bot
from random import choice as randchoice
from pprint import pprint as pp

from typing import List, Dict

from fuzzywuzzy import process

BaseCog = getattr(commands, "Cog", object)


class Say(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

    @commands.command(pass_context=True, rest_is_raw=True)
    @checks.mod()
    async def say(self, ctx, guildname: str, channelname: str, *what_to_say: str):
        """gimme a fact"""
        what_to_say = ' '.join(what_to_say)

        guilds: List[discord.Guild] = self.bot.guilds
        guilds: Dict[str, discord.Guild] = {
            g.name: g for g in guilds
        }
        pp(guilds)
        guild: discord.Guild = guilds.get(process.extractOne(guildname, list(guilds.keys()), score_cutoff=0.5)[0])
        if guild is None:
            await ctx.send("Couldn't find guild!")
            return

        channels: List[discord.TextChannel] = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
        channels: Dict[str, discord.TextChannel] = {
            c.name: c for c in channels
        }
        pp(channels)
        channel: discord.TextChannel = channels.get(process.extractOne(channelname, list(channels.keys()), score_cutoff=0.5)[0])
        if channel is None:
            await ctx.send("Couldn't find channel!")
            return

        await channel.send(what_to_say)
