from .say import Say


async def setup(bot):
    await bot.add_cog(Say(bot))
