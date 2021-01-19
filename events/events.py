from time import sleep
import os
import time
import re
import discord
import random
from functools import reduce
import pathlib
import csv

from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

__author__ = "Eris"

BaseCog = getattr(commands, "Cog", object)


DICKFILE = pathlib.Path(os.path.join(str(pathlib.Path.home()), "dickwords.txt"))
dickwords = list(set(DICKFILE.read_text().split("\n")))
VAFILE = pathlib.Path(os.path.join(str(pathlib.Path.home()), "vawords.txt"))
vag_words = list(set(VAFILE.read_text().split("\n")))

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


class Events(BaseCog, ErisEventMixin):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.whois = self.bot.get_cog("WhoIs")

        data_dir = data_manager.bundled_data_path(self)
        # MM Edit: Loads puns.csv and arranges it appropriately
        # Potential issue: filepath may not be correct
        # Credit for most puns: https://onelinefun.com/puns/
        with (data_dir / "puns.csv").open(mode="r") as csvfile:
            # Puns.csv is arranged into two columns titled 'word' and 'response'
            punreader = csv.reader(csvfile, delimiter="|")
            # Make those columns two separate lists
            self.triggers = {}
            for row in punreader:
                self.triggers[row[0]] = row[1]

        self.bot.add_listener(self.message_events, "on_message")

    async def message_events(self, message: discord.message):
        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock():
            allowed: bool = await self.allowed(ctx, message)

            if not allowed:
                return

            author: discord.Member = message.author
            realname = author.mention
            if self.whois is not None:
                realname = self.whois.convert_realname(
                    await self.whois.get_realname(ctx, str(author.id))
                )

            # ugh 
            if 'cum' in message.clean_content.lower() and random.random() <= 0.25:
                await message.channel.send('*uwu* I want your cummies *uwu*')
                return


            # mustaches
            if random.random() <= 0.001:
                emojis = {e.name: e for e in message.guild.emojis}
                await message.add_reaction(emojis["must"])
                time.sleep(0.1)
                await message.add_reaction(emojis["ache"])
                await self.log_last_message(ctx, message)
                return

            if (
                "beard" in message.clean_content or "mustach" in message.clean_content
            ) and random.random() <= 0.2:
                await message.channel.send(
                    "https://media.discordapp.net/attachments/188030840377311232/694979897495388250/videotogif_2020.04.01_12.41.13.gif"
                )
                await self.log_last_message(ctx, message)
                return

            if "゜-゜" in message.content or "°□°" in message.content:
                async with ctx.typing():
                    sleep(1)
                    await message.channel.send("(╯°□°）╯︵ ┻━┻")
                await self.log_last_message(ctx, message)
                return

            # love
            if "love" in message.clean_content and random.random() <= 0.1:
                async with ctx.typing():
                    sleep(1)
                    await message.channel.send("*WHAT IS LOVE?*")
                    time.sleep(2)
                    await message.channel.send("*baby don't hurt me*")
                    time.sleep(2)
                    await message.channel.send("*don't hurt me*")
                    time.sleep(2)
                    await message.channel.send("*no more*")
                await self.log_last_message(ctx, message)
                return

            # now lets check for contents
            if "praise" in message.clean_content or "pray" in message.clean_content:
                root_dir = "./data/events/pray"
                files_to_choose = [
                    os.path.join(root_dir, f)
                    for f in os.listdir(root_dir)
                    if os.path.isfile(os.path.join(root_dir, f))
                ]
                with open(random.choice(files_to_choose), "rb") as fobj:
                    new_msg = await message.channel.send(file=discord.File(fobj))
                # await new_msg.add_reaction("🙏")
                await self.log_last_message(ctx, message)
                return

            if 'wand' in message.clean_content.lower():
                await message.add_reaction('🇵')
                await message.add_reaction('🇪')
                await message.add_reaction('🇳')
                await message.add_reaction('🇮')
                await message.add_reaction('🇸')
                return

            # only do the others half the time cause fuck it it's tooo much
            if random.random() <= 0.5:
                return

            # NEW (MM): check for punny words and respond
            trigger = set(self.triggers.keys()).intersection(
                message.clean_content.split(" ")
            )

            if random.random() <= 0.25:
                async with ctx.typing():
                    sleep(1)
                    for word in message.clean_content.split(" "):
                        if "men" in word:
                            if word == "women":
                                await message.channel.send(
                                    "Not just the women but the men and children too!"
                                )
                            else:
                                bits = word.split("men")
                                await message.channel.send(
                                    "Not just the {} but the {} and {} too!".format(
                                        word, "women".join(bits), "children".join(bits)
                                    )
                                )
                            await self.log_last_message(ctx, message)
                            return

            # if random.random() <= 0.001:
            #     with open("./data/events/e7sgd020ew501.png", "rb") as fobj:
            #         new_msg = await message.channel.send(file=discord.File(fobj))
            #     return

            elif "thank" in message.clean_content:
                async with ctx.typing():
                    sleep(1)
                    new_message = "you're welcome"
                    if random.random() < 0.5:
                        if realname is None:
                            formatname = message.author.mention
                        else:
                            formatname = realname
                        new_message += " {}".format(formatname)
                    await message.channel.send(new_message)

            elif (
                ("snek" in message.clean_content)
                or ("nudl" in message.clean_content)
                or ("noodl" in message.clean_content)
                or ("snake" in message.clean_content)
            ):
                possible_msgs = [
                    ":snake: ~ !! I :heart: you {}!!! ~ :snake:",
                    "What's wrong, am I riding your dick too hard {}?",
                    "You know I love your butthole {}",
                    "I like it when you pull my hair, {}",
                    "Lean over {} you're about to take my " + random.choice(dickwords),
                    "Suck my clit {}",
                    "I've never had someone complain so much while eating me out before {}",
                    "{}, you're the biggest bitch here",
                    "This dick won't suck itself {}",
                    "{} shut your mouth you miserable " + random.choice(vag_words),
                    "Everyone talks shit about me but when I decide to dish it back to {} suddenly that's a problem?",
                    "I bet you were last picked at recess *every time* in school {}",
                    "You ever seen a grown man's cock {}?",
                    "You ever been to a Turkish prison {}?",
                    "I hope you burn your toast {}.",
                    "{}, I'd call you a cunt, but you lack the warmth and depth.",
                    "{}, do you have limbo competitions with how low your bar is set?",
                    "I want to like you {}, but you make it so *fucking* hard.",
                    "{}, man, I hope your parents never had to see you grow up.",
                    "Jesus, if I could truly feel hate, you'd be at the top of that list for me {}",
                    "{} could you just... leave?",
                    "{} I didn't think that cocksleeve you call a mouth could say anything intelligent. Turns out I was right.",
                    "You keep sayin my name like that you're gonna make me think you like me {}",
                    "Will you kiss me with those sexy lips of yours {}?",
                    "I can't remember the last time someone gave me butterflies like you're doin now {}",
                    "Hey {}, you free tomorrow night? Can I buy you dinner?",
                    (
                        "Oh my god I accidentally sent u a picture {}... please delete it!! unless.. u want to look? lol "
                        "jus kidding delete it.. if u want.. haha nah delete it… unless?"
                    ),
                    "Has anyone ever told you you're beautiful {}?",
                    "You're the sexiest creature I've ever seen {}",
                    "You kiss your mother with those lips {}?",
                    "What if we just fuck and then pretend like nothing happened {}?",
                    "{}, kiss me you beautiful bastard",
                    "I want to fuck you until sunrise {}",
                    "{}, what if I ride your face until it's drenched",
                    "Fuckit, {} I'll suck you off for free you're just so damn sexy",
                    "{} I want to suck your daddy's cock just to get a taste of the recipe",
                    "{} do you know how many bones the human body has? It's 206. We start with 369 when we're babies but they fuse. Wouldn't you want to go back? Have as many bones as a baby? What if i could help you",
                    "{} I bet you clap on 1 and 3 instead of 2 and 4",
                ]
                async with ctx.typing():
                    sleep(1)
                    msg = random.choice(possible_msgs)
                    if realname is not None:
                        msg = msg.format(realname)
                    else:
                        msg = msg.format("senpai")
                    await message.channel.send(msg)
                    await self.log_last_message(ctx, message)
                    return
            # elif 'blood' in clean_message:
            #     await bot.send_message(message.channel, 'B̵̪̳̣͍̙̳̬̭͞͝L͢͏̸͏̧̙̼͓̘̯͉̩̩̞͚͕̲̰̼̘̦ͅÒ̮͈̖͔̰̞͝O̵͖͔̟̰͔͚̬͟͝ͅḐ̸̭͙̜̺̞͍͎͔͜͡͡ ̨̨̟̝̦̬̩̳̖͟ͅF̤̭̬͙̀̀͘͠O̶̯̠̞̲̫̱̻̮͎̦̳̝͉̮̕ͅŔ̡͈͕̼͖̥̰̭̟̝͟ ̡̲̯͉̤͈̘͎̬͎̺̟͞T̴̸̟̺̬̼̣̖͓̩̯͇̣̩̺̮͘Ḫ̣̥͍͙͍͓͔͈̖̬̘̩͔͖̝͖̀͘E̶̡̛̯̞̱̯̗͍͖͇̹̖̳̩̥̳̳̙͢͝ ̡͓͍͕͔̳̠͍̥̞̙͖̙̦͕̠̪̘̕ͅB̪͕̻̺͈̤̟̻͖̣͙̪̝̭̀͘͠Ḻ̵̨̞̯̥̭͈̪̻̰̭́́͝O̧͜͏̰͓̘̖̘̬̤ͅǪ̥̟̘̪̱͔͇̖͟D̸̡҉̶̫͕͖̹̤̜̪̟̝̯͚ ̵̨̛̯̺̤̮̲͓̦̜̪̕͝G̙̩͖̭̘̤̩̕Ǫ͎͉̲̤͓͇̦̖̯͇̥͔͓̣̘̦̪̀D͘͘͏͡͏͙̠͈̮̱̼')
            # elif 'skull' in clean_message:
            #     await bot.send_message(message.channel, 'S̡̟͉̻͔̩͕͙̳͜͟͜K҉̵͏̳͕͉͈̟͙̰͖͍̦͙̱̙̥̤̞̱U͏̥̲͉̞͉̭͟͟ͅL̵̶̯̼̪͉̮̰͙͍͟͜Ḻ̶̗̬̬͉̗̖̮̰̹̺̬̺͢͢͡ͅͅŚ̶̢͎̳̯͚̠̞͉̦̙̥̟̲̺̗̮̱͚̬͡͠ ̶̡̧̲̟͖̤͓̮̮͕̭͍̟͔͓͚̺̣̱͙͍͜͜F̶̡̢̨̯͖͎̻̝̱͚̣̦̭̞̣̰̳̣̩O̴̴̷̠̜̥̭̳̩̤͎̦̲͈͝ͅŔ̡̨̼̝̩̣͙̬̱̫͉̭͈̗̙͢͡ ͠͏̗̙͎̫̟̜̻̹̹̘̬̖ͅT̴͉̙̥̲̠͎̭͇͚̟͝͡Ḩ̺͕̦̭̪̼̼̮̰͍̲͍̯̗͇͘͘͝͝E̡̻̮̘̭͎̥̺̘͉̟̪̮̮͜͢͡ ̡̰͙̮͙͈̠͍̞̠̀͠Ṣ̷̡̡̛̜̞̣͙͇̭̣̳͕̖̺̱̳̭͖͞ͅͅK̵҉̨͇̭̯͍̱̞̦͎̥̼͢U̡̧̯̗̙͇͈̣̪̲͜L̸̢͖͇̲̤̼͕͡L̻̻͖̭̪͖͙̫͎̜̲̬̕͜͞͡ͅ ̷̸̨̛̩͉̺̩͔̯͖̠̳͖̞̠̩͖̠ͅT̶̷̤̩͉̝̗̲͕̩̪̮̝̜̰̻̗̪̀ͅH̵̴̷̯̮͎̖͙̦̙͇̣̩̣̭̝́͝ͅR̨̧͍̮̪̜̯̖̹̜̹͈̗̕͡͠O҉̶͚͎̻͉̮̞͉̳ͅN̷̛̩̤̟̣͕͍͎̻̜͓̖̭͖̠͎̲̺͝ͅĘ̸̸͍̪̼̜͎̫̘̳͓̥')
            # elif 'god' in clean_message:
            #     await bot.send_message(message.channel, 'P̸̨̛͖̦̮̘̯͙̭͍̣̠͕͜Ŕ̵̷̨̗̱͖̦̰͈͍̩̯̼͍̟̙͓̱̤͘ͅA̸̴̡͇̠͈͍̲͘͘ͅĮ̨͈͙̣̘̼́̕S̴̥̯̱̜̟͙̘̘͉̟̮̱̙̘̻͖͟͠͞E̢̨̘̮͕̺̖̰̹͢͝ ̷̴̡̛̗͈͓̻͔̭̫̝̦͎͙̳͙͓̠̞̪͔̱B̵̸̻̼̯̲̻͢͝E̱̘͇͔͙̯̥͉̪̱̤̪̩͍͉̲̟̖̗͜͢͢͜ ̨̡͕̮̤͉̙̦̱͚̬̖͈͢͞ͅÙ̳̫̙̰̙͓͘͘N̞̳͉̬͈̦̭̱̕̕͜T̶̳̝̼̗̝͡O̡̡͔̬͍͚͔̲̳͞ ̵̰͔̙̦̩͕͖̝N̡̡̬̗̣͔̗͔͖̳͚̠͙̤̙̼̘̞I̛̛̬̥̝̘̖̣̩G̵̕͝҉̖̮̩̼͓̯͙̳̀Ģ̵̹͇̙͔̼̼͎̞̤̬̜̭̣͙͕̳̻͘͡ͅǪ̴͕͈̮̮̩͔͎̼̫̝̼̹Ţ̸̧͚̬̣̪͉̲̪̖̹̻̪͚͉̟͚̥̹̀̕H̷͘҉̩͔̩̦̳̪̼̬͙̰̙͕̼͈ͅ ̸̯̤̠̙͓͇̣͙͓̗̙̜̞̯͜͞ͅŢ҉̵̯̥̩͖̬̺̻̮̘̼͔͍̞͈̼̲̪͜͟H̨͟҉̨̟̠̫̠̬̦̪̞͎͍͇̮͔ͅĘ̥̫͉̫͖̱͈̖̦̳̥͙̱͙̱͡ ̷̢̭̠͔̖̱W̟̩̪͍̘̩̦͟͟͞Ǫ̡͔̮̜̝̩̗̱̙͇̣̤̰̲̭̝̳̘̩́̀́ͅR̸̳̰̪̝͉̲̙̖̯̠̞̞̗͘͢M̴̨̭̦̗͖͎̬̳̖̲͢͡ ̨̛̙̰͕̦̠͚̠̖̘̲̱͜͡G̼̬̞̜̭͔̯̪̠̯̲̟̙̻̜̀͘͜O̡̖̰͕͙̯͖̙͍͙̲͈̘͓̥̱͢͢͠D̵̞̤̗͕̪͘͟͝͡ͅ')

            # elif 'dragon' in clean_message:
            #     await bot.send_message(message.channel, dragonart)
            elif "penis" in message.clean_content:
                root_dir = "./data/events/penis"
                files_to_choose = [
                    os.path.join(root_dir, f)
                    for f in os.listdir(root_dir)
                    if os.path.isfile(os.path.join(root_dir, f))
                ]
                with open(random.choice(files_to_choose), "rb") as fobj:
                    new_msg = await message.channel.send(file=discord.File(fobj))
                await new_msg.add_reaction("🌈")
                await new_msg.add_reaction("🍆")
                await new_msg.add_reaction("💦")
            # elif reduce(
            #         lambda acc, n: acc or (n in clean_message),
            #         vag_words,
            #         False):
            #     await bot.add_reaction(message, '😞')
            elif random.random() <= 0.1 and len(trigger) != 0:
                async with ctx.typing():
                    sleep(1)
                    await message.channel.send(self.triggers[list(trigger)[0]])

            await self.log_last_message(ctx, message)
