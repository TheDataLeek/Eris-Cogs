from .goodbot import GoodBot, generate_handlers

def setup(bot):
    bot.add_cog(GoodBot(bot))

    goodbot, parse_reaction_add, parse_reaction_remove = generate_handlers(bot)

    bot.add_listener(goodbot, 'on_message')
    bot.add_listener(parse_reaction_add, 'on_reaction_add')
    bot.add_listener(parse_reaction_remove, 'on_reaction_remove')
