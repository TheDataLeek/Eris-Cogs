from .spoop import Spoop


def setup(bot):
    bot.add_cog(Spoop(bot))
