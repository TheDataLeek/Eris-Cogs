from .goodbot import GoodBot


def setup(bot):
    gb_instance = GoodBot(bot)
    bot.add_cog(gb_instance)
