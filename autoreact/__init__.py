from .autoreact import AutoReact


def setup(bot):
    bot.add_cog(AutoReact(bot))
