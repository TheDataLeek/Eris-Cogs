import discord
from redbot.core import commands
import random
import re

dice_format = '([0-9]+)d([0-9]+)(v[0-9])?'

class Dice:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def dice(self, ctx, roll: str):
        if not re.match(dice_format, roll):
            await self.bot.say('Please Roll dice in the form {}'.format(dice_format))
            return

        terms = re.findall(dice_format, roll)[0]
        numdice = int(terms[0])
        typedice = int(terms[1])
        dropdice = terms[2]

        rolls = [random.randint(1, typedice) for _ in range(numdice)]
        rolls.sort(key=lambda x: -x)
        if dropdice != '':
            rolls = rolls[:-int(dropdice[1:])]
        await self.bot.say('Rolling {}... {} = {}'.format(roll, sum(rolls), str(rolls)))

