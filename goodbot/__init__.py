from .goodbot import GoodBot, generate_handlers


def setup(bot):
    gb_instance = GoodBot(bot)
    bot.add_cog(gb_instance)
