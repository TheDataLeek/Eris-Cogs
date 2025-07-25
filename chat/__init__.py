from chatlib import Chat


async def setup(bot):
    cog = Chat(bot)
    await bot.add_cog(cog)
