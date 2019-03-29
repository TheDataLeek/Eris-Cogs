from .events import Spoop, generate_handler

def setup(bot):
    bot.add_cog(Spoop(bot))

    generate_handler(bot)
