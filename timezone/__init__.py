from .tz import Timezone


def setup(bot):
    bot.add_cog(Timezone(bot))
