from .minesweeper import MineSweeper


async def setup(bot):
    await bot.add_cog(MineSweeper(bot))
