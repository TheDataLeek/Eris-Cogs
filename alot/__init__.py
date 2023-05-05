from .alot import Alot


def setup(bot):
    await bot.add_cog(Alot(bot))
