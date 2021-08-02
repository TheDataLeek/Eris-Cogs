from .imdblookup import IMDBLookup


def setup(bot):
    bot.add_cog(IMDBLookup(bot))
