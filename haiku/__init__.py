from .haiku import Haiku


def setup(bot):
    bot.add_cog(Haiku(bot))
