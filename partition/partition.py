# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class Partition(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def partition(self, ctx, how_many_teams: int, *users: discord.Member):
        """
        Partitions teams
        Usage: [p]partition <Members>
        """
        if how_many_teams < 2:
            await ctx.send("Need to ask for at least two teams!")
            return

        users = [*users]
        random.shuffle(users)
        teams = [[] for i in range(how_many_teams)]
        n_members_per_team = len(users) // how_many_teams
        for team_index in range(how_many_teams):
            start = team_index * n_members_per_team
            end = (team_index + 1) * n_members_per_team
            if team_index == how_many_teams - 1:
                end = len(users) + 1
            teams[team_index] = users[start:end]

        formatted_message = ["```"]
        for i, team in enumerate(teams):
            members = sorted([m.nick or m.display_name for m in team])
            members = ", ".join(members)
            formatted_message.append(f"Team #{i + 1}: {members}")

        formatted_message.append("```")
        formatted_message = "\n".join(formatted_message)

        await ctx.send(formatted_message)
