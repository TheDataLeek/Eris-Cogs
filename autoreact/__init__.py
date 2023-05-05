from .autoreact import AutoReact


async def setup(bot):
    await bot.add_cog(AutoReact(bot))
