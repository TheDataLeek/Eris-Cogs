from .emojsplosion import EmojSplosion


async def setup(bot):
    await bot.add_cog(EmojSplosion(bot))
