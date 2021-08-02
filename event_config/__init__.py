from .event_config import EventConfig


def setup(bot):
    bot.add_cog(EventConfig(bot))
