from .steve import Steve


async def setup(bot):
    await bot.add_cog(Steve(bot))
