from .move import Move


async def setup(bot):
    await bot.add_cog(Move(bot))
