from .outofcontext import OutOfContext


async def setup(bot):
    await bot.add_cog(OutOfContext(bot))
