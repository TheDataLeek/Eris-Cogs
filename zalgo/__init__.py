from .zalgo import Zalgo


async def setup(bot):
    await bot.add_cog(Zalgo(bot))
