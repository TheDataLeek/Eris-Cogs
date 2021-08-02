from fuzzywuzzy import process, fuzz
import discord
from redbot.core import commands, checks

BaseCog = getattr(commands, "Cog", object)


class DMRole(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.mod()
    async def tell(self, ctx, rolename: str, *message: str):
        """
        Mod-only command to DM everyone who has specified role
        """
        message = " ".join(message)

        scores = sorted(
            [(r, fuzz.ratio(rolename, r.name)) for r in ctx.guild.roles],
            key=lambda tup: -tup[1],
        )
        role: discord.Role
        role, score = scores[0]

        if score < 50:
            await ctx.send("Role not found!")
            return

        for member in role.members:
            await member.send(message)

        await ctx.send("Done")
