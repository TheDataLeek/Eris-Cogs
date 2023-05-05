from .nick_prefix import NickPrefix


async def setup(bot):
    await bot.add_cog(NickPrefix(bot))
