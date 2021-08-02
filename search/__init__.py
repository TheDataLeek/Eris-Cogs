from .search import Search


def setup(bot):
    bot.add_cog(Search(bot))
