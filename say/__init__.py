from .facts import Fact

def setup(bot):
    bot.add_cog(Fact(bot))
