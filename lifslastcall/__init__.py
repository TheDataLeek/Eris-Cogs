from .lifs import Lifs


async def setup(bot):
    await bot.add_cog(Lifs(bot))
