from .no_fuck_you import NoFuckYou


async def setup(bot):
    await bot.add_cog(NoFuckYou(bot))
