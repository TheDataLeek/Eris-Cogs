from .sarcasm import Sarcasm


async def setup(bot):
    await bot.add_cog(Sarcasm(bot))
