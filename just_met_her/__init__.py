from .justmether import JustMetHer


async def setup(bot):
    await bot.add_cog(JustMetHer(bot))
