from .dm_role import DMRole


def setup(bot):
    bot.add_cog(DMRole(bot))
