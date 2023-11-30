from .roulette import Roulette


async def setup(bot):
    await bot.add_cog(Roulette(bot))
