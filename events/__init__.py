from .events import Spoop, generate_handler

def setup(bot):
    bot.add_cog(Spoop(bot))

    message_handler = generate_handler(bot)

    bot.add_listener(message_handler, 'on_message')
