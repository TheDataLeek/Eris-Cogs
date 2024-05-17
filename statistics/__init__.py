from .statistics import Statistics


async def setup(bot):
    await bot.add_cog(Statistics(bot))
