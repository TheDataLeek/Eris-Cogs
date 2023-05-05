from .venmo import Venmo


async def setup(bot):
    await bot.add_cog(Venmo(bot))
