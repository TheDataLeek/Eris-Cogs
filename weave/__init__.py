from .weave import Weave


async def setup(bot):
    await bot.add_cog(Weave(bot))
