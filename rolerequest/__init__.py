from .rolerequest import RoleRequest


async def setup(bot):
    await bot.add_cog(RoleRequest(bot))
