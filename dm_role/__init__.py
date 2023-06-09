from .dm_role import DMRole


async def setup(bot):
    await bot.add_cog(DMRole(bot))
