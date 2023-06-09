from .stonks import Stonks


async def setup(bot):
    await bot.add_cog(Stonks(bot))
