from .wiggly import Wiggle


async def setup(bot):
    await bot.add_cog(Wiggle(bot))
