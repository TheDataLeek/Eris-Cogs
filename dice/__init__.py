from .dice import Dice


def setup(bot):
    n = Dice(bot)
    bot.add_cog(n)
