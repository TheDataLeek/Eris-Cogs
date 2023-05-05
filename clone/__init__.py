from .clone import Clone


async def setup(bot):
    await bot.add_cog(Clone(bot))
