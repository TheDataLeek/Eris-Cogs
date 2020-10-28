from .move import Move


def setup(bot):
    bot.add_cog(Move(bot))
