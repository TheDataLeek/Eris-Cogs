from .secretsanta import SecretSanta


async def setup(bot):
    await bot.add_cog(SecretSanta(bot))
