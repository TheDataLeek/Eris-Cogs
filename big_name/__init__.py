from .big_name import BigName


async def setup(bot):
    await bot.add_cog(BigName(bot))
