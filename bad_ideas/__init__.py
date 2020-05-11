from .bad_ideas import BigName, Clone, Weave


def setup(bot):
    bot.add_cog(BigName(bot))
    bot.add_cog(Clone(bot))
    bot.add_cog(Weave(bot))
