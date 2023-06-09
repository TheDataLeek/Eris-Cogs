from .grammar import Grammar


async def setup(bot):
    await bot.add_cog(Grammar(bot))
