from .quotes import Quotes


async def setup(bot):
    await bot.add_cog(Quotes(bot))
