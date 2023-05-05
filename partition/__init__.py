from .partition import Partition


async def setup(bot):
    await bot.add_cog(Partition(bot))
