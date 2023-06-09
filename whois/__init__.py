from .whois import WhoIs


async def setup(bot):
    await bot.add_cog(WhoIs(bot))
