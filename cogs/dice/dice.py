import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import random
import re

dice_format = '([0-9]+)d([0-9]+)(v[0-9])?'

class Dice:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def zalgo(self, ctx, roll: str):
        if not re.match(dice_format, roll):
            await self.bot.say('Please Roll dice in the form {}'.format(dice_format))

        terms = re.findall(dice_format, roll)
        numdice = int(terms.group(1))
        typedice = int(terms.group(2))
        dropdice = terms.group(2)

        rolls = [random.randint(1, typedice) for _ in range(numdice)]
        rolls.sort()
        if dropdice is not None:
            rolls = rolls[:-int(dropdice)]
        await self.bot.say('Rolling {}... {} = {}'.format(roll, sum(rolls), str(rolls)))


def setup(bot):
    n = Dice(bot)
    bot.add_cog(n)

