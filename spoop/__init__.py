from .spoop import Spoop


async def setup(bot):
    await bot.add_cog(Spoop(bot))
