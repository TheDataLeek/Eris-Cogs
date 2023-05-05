from .search import Search


async def setup(bot):
    await bot.add_cog(Search(bot))
