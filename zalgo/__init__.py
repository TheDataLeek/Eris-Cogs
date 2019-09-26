from .zalgo import Zalgo

def setup(bot):
    bot.add_cog(Zalgo(bot))

