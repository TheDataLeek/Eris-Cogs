from .venmo import Venmo


def setup(bot):
    bot.add_cog(Venmo(bot))
