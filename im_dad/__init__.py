from .imdad import ImDad


async def setup(bot):
    await bot.add_cog(ImDad(bot))
