from .events import Spoop, Events


def setup(bot):
    bot.add_cog(Spoop(bot))
    bot.add_cog(Events(bot))
