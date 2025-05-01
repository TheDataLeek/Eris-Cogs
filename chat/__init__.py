from .chatlib import Chat


async def setup(bot):
    await bot.add_cog(Chat(bot))
