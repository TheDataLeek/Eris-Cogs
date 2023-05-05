from .haiku import Haiku


async def setup(bot):
    await bot.add_cog(Haiku(bot))
