import discord
from discord.ext import commands
import random

dragonart = """
```
                                                 /===-_---~~~~~~~~~------____
                                                |===-~___                _,-'
                 -==\\                         `//~\\   ~~~~`---.___.-~~
             ______-==|                         | |  \\           _-~`
       __--~~~  ,-/-==\\                        | |   `\        ,'
    _-~       /'    |  \\                      / /      \      /
  .'        /       |   \\                   /' /        \   /'
 /  ____  /         |    \`\.__/-~~ ~ \ _ _/'  /          \/'
/-'~    ~~~~~---__  |     ~-/~         ( )   /'        _--~`
                  \_|      /        _)   ;  ),   __--~~
                    '~~--_/      _-~/-  / \   '-~ \
                   {\__--_/}    / \\_>- )<__\      \
                   /'   (_/  _-~  | |__>--<__|      |
                  |0  0 _/) )-~     | |__>--<__|     |
                  / /~ ,_/       / /__>---<__/      |
                 o o _//        /-~_>---<__-~      /
                 (^(~          /~_>---<__-      _-~
                ,/|           /__>--<__/     _-~
             ,//('(          |__>--<__|     /                  .----_
            ( ( '))          |__>--<__|    |                 /' _---_~\
         `-)) )) (           |__>--<__|    |               /'  /     ~\`\
        ,/,'//( (             \__>--<__\    \            /'  //        ||
      ,( ( ((, ))              ~-__>--<_~-_  ~--____---~' _/'/        /'
    `~/  )` ) ,/|                 ~-_~>--<_/-__       __-~ _/
  ._-~//( )/ )) `                    ~~-'_/_/ /~~~~~~~__--~
   ;'( ')/ ,)(                              ~~~~~~~~~~
  ' ') '( (/
    '   '  `
```
"""

def setup(bot):
    async def message_events(message):
        # DO NOT RESPOND TO SELF MESSAGES
        if bot.user.id == message.author.id or message.content.startswith('.zalgo'):
            return

        if 'zeb' in message.clean_content.lower():
            await bot.send_message(message.channel, 'Daisuki, Zeb-kun!')
            await bot.send_message(message.channel, ':eggplant: :eggplant: :sweat_drops: :sweat_drops:')

        elif 'masters' in [x.name.lower() for x in message.author.roles] and random.random() <= 0.05:
            await bot.send_message(message.channel, 'PIPE DOWN NIGGA')

        elif 'snek' in message.clean_content.lower():
            await bot.send_message(message.channel, ':snake: ~ !! I :heart: you senpai !! ~ :snake:')
        elif 'blood' in message.clean_content.lower():
            await bot.send_message(message.channel, 'B̵̪̳̣͍̙̳̬̭͞͝L͢͏̸͏̧̙̼͓̘̯͉̩̩̞͚͕̲̰̼̘̦ͅÒ̮͈̖͔̰̞͝O̵͖͔̟̰͔͚̬͟͝ͅḐ̸̭͙̜̺̞͍͎͔͜͡͡ ̨̨̟̝̦̬̩̳̖͟ͅF̤̭̬͙̀̀͘͠O̶̯̠̞̲̫̱̻̮͎̦̳̝͉̮̕ͅŔ̡͈͕̼͖̥̰̭̟̝͟ ̡̲̯͉̤͈̘͎̬͎̺̟͞T̴̸̟̺̬̼̣̖͓̩̯͇̣̩̺̮͘Ḫ̣̥͍͙͍͓͔͈̖̬̘̩͔͖̝͖̀͘E̶̡̛̯̞̱̯̗͍͖͇̹̖̳̩̥̳̳̙͢͝ ̡͓͍͕͔̳̠͍̥̞̙͖̙̦͕̠̪̘̕ͅB̪͕̻̺͈̤̟̻͖̣͙̪̝̭̀͘͠Ḻ̵̨̞̯̥̭͈̪̻̰̭́́͝O̧͜͏̰͓̘̖̘̬̤ͅǪ̥̟̘̪̱͔͇̖͟D̸̡҉̶̫͕͖̹̤̜̪̟̝̯͚ ̵̨̛̯̺̤̮̲͓̦̜̪̕͝G̙̩͖̭̘̤̩̕Ǫ͎͉̲̤͓͇̦̖̯͇̥͔͓̣̘̦̪̀D͘͘͏͡͏͙̠͈̮̱̼')
        elif 'skull' in message.clean_content.lower():
            await bot.send_message(message.channel, 'S̡̟͉̻͔̩͕͙̳͜͟͜K҉̵͏̳͕͉͈̟͙̰͖͍̦͙̱̙̥̤̞̱U͏̥̲͉̞͉̭͟͟ͅL̵̶̯̼̪͉̮̰͙͍͟͜Ḻ̶̗̬̬͉̗̖̮̰̹̺̬̺͢͢͡ͅͅŚ̶̢͎̳̯͚̠̞͉̦̙̥̟̲̺̗̮̱͚̬͡͠ ̶̡̧̲̟͖̤͓̮̮͕̭͍̟͔͓͚̺̣̱͙͍͜͜F̶̡̢̨̯͖͎̻̝̱͚̣̦̭̞̣̰̳̣̩O̴̴̷̠̜̥̭̳̩̤͎̦̲͈͝ͅŔ̡̨̼̝̩̣͙̬̱̫͉̭͈̗̙͢͡ ͠͏̗̙͎̫̟̜̻̹̹̘̬̖ͅT̴͉̙̥̲̠͎̭͇͚̟͝͡Ḩ̺͕̦̭̪̼̼̮̰͍̲͍̯̗͇͘͘͝͝E̡̻̮̘̭͎̥̺̘͉̟̪̮̮͜͢͡ ̡̰͙̮͙͈̠͍̞̠̀͠Ṣ̷̡̡̛̜̞̣͙͇̭̣̳͕̖̺̱̳̭͖͞ͅͅK̵҉̨͇̭̯͍̱̞̦͎̥̼͢U̡̧̯̗̙͇͈̣̪̲͜L̸̢͖͇̲̤̼͕͡L̻̻͖̭̪͖͙̫͎̜̲̬̕͜͞͡ͅ ̷̸̨̛̩͉̺̩͔̯͖̠̳͖̞̠̩͖̠ͅT̶̷̤̩͉̝̗̲͕̩̪̮̝̜̰̻̗̪̀ͅH̵̴̷̯̮͎̖͙̦̙͇̣̩̣̭̝́͝ͅR̨̧͍̮̪̜̯̖̹̜̹͈̗̕͡͠O҉̶͚͎̻͉̮̞͉̳ͅN̷̛̩̤̟̣͕͍͎̻̜͓̖̭͖̠͎̲̺͝ͅĘ̸̸͍̪̼̜͎̫̘̳͓̥')
        elif 'god' in message.clean_content.lower():
            await bot.send_message(message.channel, 'P̸̨̛͖̦̮̘̯͙̭͍̣̠͕͜Ŕ̵̷̨̗̱͖̦̰͈͍̩̯̼͍̟̙͓̱̤͘ͅA̸̴̡͇̠͈͍̲͘͘ͅĮ̨͈͙̣̘̼́̕S̴̥̯̱̜̟͙̘̘͉̟̮̱̙̘̻͖͟͠͞E̢̨̘̮͕̺̖̰̹͢͝ ̷̴̡̛̗͈͓̻͔̭̫̝̦͎͙̳͙͓̠̞̪͔̱B̵̸̻̼̯̲̻͢͝E̱̘͇͔͙̯̥͉̪̱̤̪̩͍͉̲̟̖̗͜͢͢͜ ̨̡͕̮̤͉̙̦̱͚̬̖͈͢͞ͅÙ̳̫̙̰̙͓͘͘N̞̳͉̬͈̦̭̱̕̕͜T̶̳̝̼̗̝͡O̡̡͔̬͍͚͔̲̳͞ ̵̰͔̙̦̩͕͖̝N̡̡̬̗̣͔̗͔͖̳͚̠͙̤̙̼̘̞I̛̛̬̥̝̘̖̣̩G̵̕͝҉̖̮̩̼͓̯͙̳̀Ģ̵̹͇̙͔̼̼͎̞̤̬̜̭̣͙͕̳̻͘͡ͅǪ̴͕͈̮̮̩͔͎̼̫̝̼̹Ţ̸̧͚̬̣̪͉̲̪̖̹̻̪͚͉̟͚̥̹̀̕H̷͘҉̩͔̩̦̳̪̼̬͙̰̙͕̼͈ͅ ̸̯̤̠̙͓͇̣͙͓̗̙̜̞̯͜͞ͅŢ҉̵̯̥̩͖̬̺̻̮̘̼͔͍̞͈̼̲̪͜͟H̨͟҉̨̟̠̫̠̬̦̪̞͎͍͇̮͔ͅĘ̥̫͉̫͖̱͈̖̦̳̥͙̱͙̱͡ ̷̢̭̠͔̖̱W̟̩̪͍̘̩̦͟͟͞Ǫ̡͔̮̜̝̩̗̱̙͇̣̤̰̲̭̝̳̘̩́̀́ͅR̸̳̰̪̝͉̲̙̖̯̠̞̞̗͘͢M̴̨̭̦̗͖͎̬̳̖̲͢͡ ̨̛̙̰͕̦̠͚̠̖̘̲̱͜͡G̼̬̞̜̭͔̯̪̠̯̲̟̙̻̜̀͘͜O̡̖̰͕͙̯͖̙͍͙̲͈̘͓̥̱͢͢͠D̵̞̤̗͕̪͘͟͝͡ͅ')

        elif 'dragon' in message.clean_content.lower():
            await bot.send_message(message.channel, dragonart)

    bot.add_listener(message_events, 'on_message')

