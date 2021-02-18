from .rolerequest import RoleRequest

def setup(bot):
    bot.add_cog(RoleRequest(bot))

