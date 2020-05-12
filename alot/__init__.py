from .alot import Alot


def setup(bot):
    bot.add_cog(Alot(bot))
