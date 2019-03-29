from .sarcasm import Sarcasm

def setup(bot):
    bot.add_cog(Sarcasm(bot))
