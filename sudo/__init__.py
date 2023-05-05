from .sudo import Sudo


async def setup(bot):
    await bot.add_cog(Sudo(bot))
