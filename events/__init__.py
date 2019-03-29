from .events import Spoop, message_events

def setup(bot):
    bot.add_cog(Spoop(bot))
    bot.add_listener(message_events, 'on_message')
