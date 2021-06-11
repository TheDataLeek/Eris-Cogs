from .fires import Fires


def setup(bot):
    bot.add_cog(Fires(bot))
