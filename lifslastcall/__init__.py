from .lifs import Lifs


def setup(bot):
    bot.add_cog(Lifs(bot))
