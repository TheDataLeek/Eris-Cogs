from .goodbot import GoodBot


async def setup(bot):
    gb_instance = GoodBot(bot)
    await bot.add_cog(gb_instance)
