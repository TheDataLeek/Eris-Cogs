from .jolly import Jolly


def setup(bot):
    bot.add_cog(Jolly(bot))
