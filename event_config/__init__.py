from .event_config import EventConfig


async def setup(bot):
    await bot.add_cog(EventConfig(bot))
