from .facts import Fact


async def setup(bot):
    await bot.add_cog(Fact(bot))
