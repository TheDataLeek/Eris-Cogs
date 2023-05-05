from .alot import Alot


async def setup(bot):
    await bot.add_cog(Alot(bot))
