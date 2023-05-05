from .dragon import Dragon


async def setup(bot):
    await bot.add_cog(Dragon(bot))
