from .bad_ideas import BigName, Clone


def setup(bot):
    bot.add_cog(BigName(bot))
    bot.add_cog(Clone(bot))
