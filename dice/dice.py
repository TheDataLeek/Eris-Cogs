import discord
from redbot.core import commands
import random
import re

BaseCog = getattr(commands, "Cog", object)

dice_format = '([0-9]+)d([0-9]+)(v[0-9])?'

class Dice(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def dice(self, ctx, roll: str):
        """ Roll dice in the format '([0-9]+)d([0-9]+)(v([0-9]))?' """
        if not re.match(dice_format, roll):
            return

        match = re.match(dice_format, roll)

        if match.group(1) is None or match.group(2) is None:
            await ctx.send('Please use the correct format, ex: 4d6v1')
            return

        numdice = int(match.group(1))
        typedice = int(match.group(2))

        rolls = [random.randint(1, typedice) for _ in range(numdice)]
        rolls.sort(key=lambda x: -x)

        if match.group(4) is not None:
            rolls = rolls[:-int(match.group(4))]

        await ctx.send('Rolling {}... {} = {}'.format(roll, sum(rolls), str(rolls)))

