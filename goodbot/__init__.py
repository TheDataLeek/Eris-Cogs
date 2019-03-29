from .goodbot import GoodBot, generate_handlers

def setup(bot):
    gb_instance = GoodBot(bot)
    bot.add_cog(gb_instance)

    goodbot, parse_reaction_add, parse_reaction_remove = generate_handlers(bot, gb_instance)

    bot.add_listener(goodbot, 'on_message')
    bot.add_listener(parse_reaction_add, 'on_reaction_add')
    bot.add_listener(parse_reaction_remove, 'on_reaction_remove')
