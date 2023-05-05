from .suggest import Suggest


async def setup(bot):
    await bot.add_cog(Suggest(bot))
