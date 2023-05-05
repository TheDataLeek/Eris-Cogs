from .december import December


async def setup(bot):
    await bot.add_cog(December(bot))
