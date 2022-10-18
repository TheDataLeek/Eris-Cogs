from .partition import Partition


def setup(bot):
    bot.add_cog(Partition(bot))
