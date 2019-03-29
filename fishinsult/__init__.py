from .fishinsult import Insult

def setup(bot):
    bot.add_cog(Insult(bot))
