from .big_text import BigText


async def setup(bot):
    await bot.add_cog(BigText(bot))
