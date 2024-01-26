from .usage import Usage


async def setup(bot):
    await bot.add_cog(Usage(bot))
