# stdlib
import random
import re

# third party
from redbot.core import commands, bot

BaseCog = getattr(commands, "Cog", object)


class Dice(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance
        self.dice_regex = re.compile("([0-9]+)d([0-9]+)(v[0-9])?", flags=re.IGNORECASE)

    @commands.command()
    async def dice(self, ctx, roll: str):
        """
        Rolls arbitrary dice!
        Usage: [p]dice '([0-9]+)d([0-9]+)(v[0-9])?'
        Example: [p]dice 4d6v1
        """
        match = self.dice_regex.match(roll)

        if match is None or match.group(1) is None or match.group(2) is None:
            await self.bot.send_help_for(ctx, self.dice)
            return

        numdice = int(match.group(1))
        typedice = int(match.group(2))

        rolls = [random.randint(1, typedice) for _ in range(numdice)]
        rolls.sort(key=lambda x: -x)

        if match.group(3) is not None:
            rolls = rolls[: -int(match.group(3)[1:])]

        formatted_rolls = " + ".join(str(r) for r in rolls)

        await ctx.send(f"Rolling {roll}... {sum(rolls)} ({formatted_rolls})")
