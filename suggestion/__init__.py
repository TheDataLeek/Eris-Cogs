from .suggest import Suggest


def setup(bot):
    bot.add_cog(Suggest(bot))
