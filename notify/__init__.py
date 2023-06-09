from .notify import Notify


async def setup(bot):
    await bot.add_cog(Notify(bot))
