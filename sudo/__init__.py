from .sudo import Sudo


def setup(bot):
    bot.add_cog(Sudo(bot))
