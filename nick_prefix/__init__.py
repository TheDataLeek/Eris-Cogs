from .nick_prefix import NickPrefix


def setup(bot):
    bot.add_cog(NickPrefix(bot))
