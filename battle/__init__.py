from .battle import Battle


def setup(bot):
    bot.add_cog(Battle(bot))

