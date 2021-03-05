from .quotes import Quotes


def setup(bot):
    bot.add_cog(Quotes(bot))
