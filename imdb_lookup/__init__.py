from .imdblookup import IMDBLookup


async def setup(bot):
    await bot.add_cog(IMDBLookup(bot))
