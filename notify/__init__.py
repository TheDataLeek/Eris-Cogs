from .notify import Notify

def setup(bot):
    bot.add_cog(Notify(bot))
