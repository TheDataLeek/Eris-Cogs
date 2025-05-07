from .bluesky_reposter import BlueskyReposter


async def setup(bot):
    await bot.add_cog(BlueskyReposter(bot))
