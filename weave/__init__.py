from .weave import Weave


def setup(bot):
    bot.add_cog(Weave(bot))
