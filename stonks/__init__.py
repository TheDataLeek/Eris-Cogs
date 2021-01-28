from .stonks import Stonks


def setup(bot):
    bot.add_cog(Stonks(bot))
