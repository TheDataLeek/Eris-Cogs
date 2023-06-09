from .battle import Battle


async def setup(bot):
    await bot.add_cog(Battle(bot))
