from .mtg import MTG


async def setup(bot):
    await bot.add_cog(MTG(bot))
