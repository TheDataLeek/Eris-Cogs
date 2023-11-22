from .hostinfo import HostInfo


async def setup(bot):
    await bot.add_cog(HostInfo(bot))
