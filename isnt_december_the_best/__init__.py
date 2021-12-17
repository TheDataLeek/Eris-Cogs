from .december import December


def setup(bot):
    bot.add_cog(December(bot))
