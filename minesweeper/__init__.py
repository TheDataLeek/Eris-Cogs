from .minesweeper import MineSweeper


def setup(bot):
    bot.add_cog(MineSweeper(bot))
