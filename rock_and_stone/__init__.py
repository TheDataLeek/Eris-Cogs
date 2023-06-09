from .rock_and_stone import RockAndStone


async def setup(bot):
    await bot.add_cog(RockAndStone(bot))
