import os
import discord
from discord.ext import commands
import random
from functools import reduce

import sqlite3
import pathlib


WHOFILE = os.path.join(str(pathlib.Path.home()), 'whois.db')

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

dickwords = [
    'dick',
    'chode',
    'schlong',
    'unit',
    'member',
    'johnson',
    'my little friend',
    'pocket weasel',
    'sausage',
    'man meat'
]

dickwords += [
    'adolph',
    'albino Cave Dweller',
    'baby-arm',
    'baby-maker',
    'baloney pony',
    'beaver basher',
    'beef whistle',
    'bell on a pole',
    'bishop',
    'bob Dole',
    'boomstick',
    'braciole',
    'bratwurst',
    'burrito',
    'candle',
    'choad',
    'chopper',
    'chub',
    'chubby',
    'cock',
    'cranny axe',
    'cum gun',
    'custard launcher',
    'dagger',
    'deep-V diver',
    'dick',
    'dickie',
    'ding dong',
    'mcdork',
    'dink',
    'dipstick',
    'disco stick',
    'dog head',
    'dong',
    'donger',
    'dork',
    'dragon',
    'drum stick',
    'dude piston',
    'easy Rider',
    'eggroll',
    'excalibur',
    'fang',
    'ferret',
    'fire hose',
    'flesh flute',
    'flesh tower',
    'froto',
    'fuck rod',
    'fudge sickle',
    'fun stick',
    'gigi',
    'groin',
    'heat-seeking moisture missile',
    'hog',
    'jackhammer',
    'jimmy',
    'john',
    'john Thomas',
    'johnson',
    'joystick',
    'junk',
    'kickstand',
    'king sebastian',
    'knob',
    'krull the warrior king',
    'lap rocket',
    'leaky hose',
    'lingam',
    'little Bob',
    'little Elvis',
    'lizard',
    'longfellow',
    'love muscle',
    'love rod',
    'love stick',
    'luigi',
    'manhood',
    'mayo shooting hotdog gun',
    'meat constrictor',
    'meat injection',
    'meat popsicle',
    'meat stick',
    'meat thermometer',
    'member',
    'meter long king kong dong',
    'microphone',
    'middle stump',
    'moisture and heat seeking venomous throbbing python of love',
    'mr. Knish',
    'mushroom head',
    'mutton',
    'netherrod',
    'old boy',
    'old fellow',
    'old man',
    'one-eyed monster',
    'one-eyed snake',
    'one-eyed trouser-snake',
    'one-eyed wonder weasel',
    'one-eyed yogurt slinger',
    'pecker',
    'pedro',
    'peepee',
    'percy',
    'peter',
    'pied Piper',
    'pig skin bus',
    'pink oboe',
    'piss weasle',
    'piston',
    'plug',
    'pnor',
    'poinswatter',
    'popeye',
    'pork sword',
    'prick',
    'private eye',
    'private part',
    'purple-headed yogurt flinger',
    'purple-helmeted warrior of love',
    'quiver bone',
    'ramburglar',
    'rod',
    'rod of pleasure',
    'roundhead',
    'sausage',
    'schlong',
    'dongadoodle',
    'schmeckel',
    'schmuck, shmuck',
    'schnitzel',
    'schwanz',
    'schwartz',
    'sebastianic sword',
    'shaft',
    'short arm',
    'single barrelled pump action bollock yogurt shotgun',
    'skin flute',
    'soldier',
    'spawn hammer',
    'steamin’ semen truck',
    'stick shift',
    'surfboard',
    'tallywhacker',
    'tan Bannana',
    'tassle',
    'third leg',
    'thumper',
    'thunderbird',
    'thundersword',
    'tinker',
    'todger',
    'tonk',
    'tool',
    'trouser snake',
    'tubesteak',
    'twig',
    'twig & berries',
    'twinkie',
    'vein',
    'wand',
    'wang',
    'wang doodle',
    'wanger',
    'wee wee',
    'whoopie stick',
    'wick',
    'wiener',
    'wiener Schnitzel',
    'willy',
    'wing dang doodle',
    'winkie',
    'yingyang',
    'yogurt gun'
]

vag_words = [
    'vag',
    'vajayjay',
    'box',
    'nether regions',
    'lady business',
    'lady v',
    'hoo-haw',
    'cha-cha',
    'lady bits',
    'crotch',
    'muff',
    'kitty',
    'cooch',
    'cooter',
    'snatch',
    'snapper',
    'beaver',
    'cookie',
    'cupcake',
    'coin purse',
    'lady flower',
    'honey pot',
    'poon',
    'punani',
    'twat',
    'gash',
    'banana basket',
    'flower pot',
    'fine china',
    'juice box',
    'pink panther',
    'hot pocket',
    'bikini bizkit',
    'penis fly trap',
    'vertical smile',
    'dew flaps',
    'flaming lips',
    'puff pillow',
    'notorious v.a.g.',
    'furburger',
    'bearded clam',
    'sausage wallet',
    'panty hamster',
    'meat curtains',
    'penis garage',
    'ink taco',
    'axe wound',
    'penis snuggie',
    'pussy',
    'cunt'
]

dickwords = list(set(dickwords))

yandere = [
    'I *see* you...',
    'Have you forgotten about me?',
    'I missed you last night.',
    'Where have you been?',
    "Don't try to run from me.",
    'I can always find you.',
    'Are you feeling ok?',
    'Hiding only delays the inevitable.',
    'Did you think that would work?',
    "I'm *always* watching",
    "Do you think I've forgotten about what you did?",
    'Hush. Only dreams now.',
    'Are you still there?',
    'Why are you like this',
    "What do you think you're doing?"
    "I love you, in my own crazy, crazy way....",
    "Remember I will always love you, as I claw your fucking throat away. It will end no other way.",
    "Okay, okay... OKAY, okay!",
    "You need to stop it now...",
    "Say that you want me every day",
    "Say that you want me in every way",
    "Say that you need me",
    "Got me trippin' super psycho love"
    "Aim, pull the trigger",
    "Feel the pain getting bigger",
    "Go insane from the bitter feeling",
    "If you would sit oh so close to me, that would be nice like it's supposed to be, if you don't, I'll slit your "
    "throat so won't u please b nice?",
    "...And yes, it's true, I don't have as many friends as you, but I think you're nice and maybe we could be friends! "
    "And if you say no, you're toast...",
    "My hate is safer.",
    "Nobody's gonna take you away from me. Not even me, see? I'll kill me before that happens.",
    "Well, what am I supposed to do? You won't answer my calls, you change your number, I'm not going to be ignored, {}!",
    "Careful, what you do 'cause god is watching your every move...",
    "{}, give me your answer, do, I'm half crazy all for the love of you.",
    "{}, do you know what would happen to you if you ever step out on me?",
    "STOP IT!",
    "Heaven has no rage like love to hatred turned, nor hell a fury like a woman scorned.",
    "I was the whining stranger a fool in love with time to kill",
    "Hellfire, Dark fire, now gypsy, it's your turn, choose me or your pyre, be mine or you will burn!",
    "Come now, surely we can be friends! I know so much about you. I love you, look at everything I've done for you. "
    "You'd be nothing without me! Why won't you answer me?! I bet you're busy talking to some fucking slut. Fucking "
    "skank... Is she hotter than me? Would you fuck me? Are you gay!?",
    "If you were here, I'd whisper sweet nothings in your ear, and appeal to all your fears. If you were mine, if you "
    "were only mine I'd bring you so much further down and twist your mind until the end of time. You will never "
    "realise what darkness lies inside my mind",
    "You will never be held against your will by your crazy stalker yandere girlfriend for a week while being chained "
    "to a chair and being fed by her as well as having her help you pee and also she tries to kill what litte friends "
    "you have.",
    "Your attitude was the cause; you got me stressin'. Soon as I open up the door, with your jealous questions like "
    "\"Where can I be?\" You're killing me with your jealousy now my ambition's to be free, I can't breathe 'cause soon "
    "as I leave, it's like a trap. I hear you callin' me to come back...",
    "I'll step on you, tie you up, beat you up, kick you, be a cocktease, hang you, but that's just how I express my "
    "love",
    "{} will be mine. It's not that I'm a jealous girl! I JUST DON'T LIKE OTHER PEOPLE TOUCHING MY THINGS!!",
    "I can't use what I can't abuse, "
    "And I can't stop when it comes to you..., "
    "You burned me out, but I'm back at your door, "
    "Like Joan of Arc coming back for more, "
    "I nearly died, "
    "I came to cut you up, "
    "I came to knock you down, "
    "I came around to tear your little world apart, "
    "I came to shut you up, "
    "I came to drag you down, "
    "I came around to tear your little world apart, "
    "And break your soul apart. ",
    "Say that you love me, and maybe I won't have to kill you!",
    "I'LL HAVE SEX WITH YOUR DEAD BODY!",
    "You can't escape my love, {}.",
    "TELL ME I'M PRETTY!",
    "You're going to LOVE ME!",
    "I want to mix our blood "
    "and put it in the ground "
    "so you can never leave. "
    "I want to earn your trust, "
    "your faith, your heart. "
    "You'll never be deceived",
    "How the hell have you not learned yet that I am a jealous psychopath?",
    "Do you want to go?! ... How badly you want to leave my grasp?! ... You can't. You can't!! I won't have it!! "
    "I WON'T LET YOU!!",
    "Crept through the curtains, as quick as the cold wind, "
    "slowly exploring the room where you sleep. "
    "The stare of your portrait, the passing of your scent, "
    "left me no choice but to stay. "
    "I will dissolve into the dark beneath your bed. "
    "My hands will wait for a taste of your skin.",
    "I have been looking for you for a long time, love, but it's always this way. You always try to escape me, always "
    "try to leave me, and you never stay, never, and I don't understand why. I love you best. I always loved you "
    "best, even when you didn't remember my name: you'll remember me eventually, won't you? No one else will ever "
    "love you as much as or the way I love you.",
    "There is nothing I won't do for Senpai. I won't let anyone come between us. I don't care what I have to do. I "
    "don't care who I have to hurt. I don't care whose blood I have to spill. I won't let anyone take him from me. "
    "Nothing else matters. No one else matters. Senpai. Will. Be. Mine....He doesn't have a choice.",
    "I yearn for your love, I yearn for your blood. The blaze in my heart lies deep as roots in this ground. "
    "Take me into you, take my hand, or I'll kill again.",
    "When love is not madness, it is not love.",
    "{}... Do you know why I'm doing this...? Why I keep fighting to keep you around? I'm doing this...because "
    "you're special, {}. You're the only one who understands me. You're the only one who's any fun to play with "
    "anymore. .. No... That's not JUST it. I... I... I'm doing this because I care about you, {}! I care about you "
    "more than anybody else! I'm not ready for this to end. I'm not ready for you to leave. I'm not ready to say "
    "goodbye to someone like you again... So, please...STOP doing this...AND JUST LET ME WIN!!!",
    "I can't believe you really did it. I was just teasing. I loved you. ...Of course, I was coming up here to kill "
    "ya.",
    "I love you. I mean, I'm still gonna kill you, but man, oh, man, am I gonna feel bad about it!",
    "By the way, I'll ask you one more time...you love me, right? Just try to say you don't love me. I'll rip you "
    "and this house apart right here, right now. If you die, you'll be mine forever, because you'll live on in my "
    "heart as a memory forever. HURRY UP AND ANSWER ME!",
    "Oh, {}, {}, {}! You know, I should shoot you in a jealous rage. Now wouldn't that be sexy?",
    "Carved your name across three counties, "
    "ground it in with bloody hides. "
    "Their broken necks will line the ditch, "
    "'till you stop it- stop it- stop it- stop it- stop it, "
    "stop this madness, "
    "I want you....",
    "Never stick your dick in crazy.",
    "I'll be watching over you, I'll be there forever, so don't think you're alone, darling :heart:",
    "I'm crazy?! What's crazy is that this world refuses to let me be with you!!!",
    "I command, that you'll love me and let me protect you!",
    "Despair of tomorrow! Despair of the unknown!  Despair of my love!",
    "I imagine many things most of these \"things\" has something to do with you. Touch you, love you, kiss you, hug "
    "you, smell you, squeeze you, break you, crush you, own you, until your soul, every bloody bit of your soul, is "
    "mine.",
    "Catching your heart with my left heart, I smile while you shout and scream, why do you react like this? Didn't "
    "you tell me you'd do anything for me? The scissors are stained in blood now. But at least, finally your heart "
    "will be mine.",
    "I'll cut of your hand, so I can hold it forever!",
    "Friends are like balloons, when you stab them they die!",
    "A half moon..., a bright half and a dark half, just like me.",
    "Do you like my cookies?  They're made just for you.  A little bit of sugar but a lots of poison too.",
    "What is mine is only mine.  And I'm ready to kill for it.",
    "Do you think if you ignore me, I would stop following you?  Do you think if you would get some help, I would "
    "back down and give up?  Or have you ever thought, if you hide somewhere, I'd never find you in this world? "
    "Oh no no no my dear!",
    "Roses are red, handcuffs are naughty, if you ever left me, they'd never find your body.",
    "If you aren't all mine I can't stand it!",
    "I was your cure, and you we're my disease, I was saving you, an you were killing me.",
    "The only way to stop the pain, is to destroy the source of it.",
    "If I can not have you, no one can.",
    "I will forgive you, but there is a price to pay.",
    "Don't let go, don't leave me alone, whit myself, the voices won't leave me alone!",
    "If you love something set it free..., if it doesn't come back, hunt it down and kill it.",
    "It's not stalking it is called taking an interest",
    "You are mine, no one except me can have you!",
    "Whatever you do, whenever you hide, wherever you try to escape from me, you should accept the simple fact, "
    "I'm always right behind you.",
    "You'll love me forever and ever, right?  And you'll never think about anything but my own happiness, right?!",
    "Catching your heart whit my left hand, I smile at you while you shout and cry, why do you react like this? "
    "Didn't you tell me you'd do anything for me?  The scissors are stained now.  But at least, finally, your "
    "heart will be mine.",
    "Twinkle twinkle little star, You're my man, oh yes you are!  Soon you'll want to marry me, or I'll hang you "
    "from the highest tree. Twinkle twinkle sweetie pie :heart:"
]


def get_realname(userid: str):
    con = sqlite3.connect(WHOFILE)
    c = con.cursor()
    c.execute(
        'SELECT name '
        'FROM usernames '
        'WHERE userid=?',
        (userid,)
    )
    name = c.fetchall()
    con.close()
    if len(name) == 0:
        return None
    else:
        return name[0][0]


class Spoop(object):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def spoop(self, ctx, user: discord.Member=None):
        if 'masters' not in [x.name.lower() for x in ctx.message.author.roles]:
            return

        realname = get_realname(user.id)

        if user is None:
            await self.bot.send_message(ctx.message.author, 'Stop being such a fuckup')
            await self.bot.delete_message(ctx.message)
            return

        new_message = random.choice(yandere)
        if realname is None:
            formatname = user.mention
        else:
            formatname = realname
        new_message = ' '.join(x.format(formatname)
                               for x in new_message.split(' '))
        await self.bot.send_message(user, new_message)
        await self.bot.delete_message(ctx.message)


def setup(bot):
    async def message_events(message):
        # DO NOT RESPOND TO SELF MESSAGES
        if bot.user.id == message.author.id or message.content.startswith('.'):
            return

        # BLACKLIST CHANNELS
        blacklist = [
            'news',
            'rpg',
            'events',
            'recommends'
        ]

        # IF DM's
        if message.channel.name is None:
            if random.random() < 0.11:
                realname = get_realname(message.author.id)
                if realname is None:
                    formatname = message.author.mention
                else:
                    formatname = realname
                new_message = random.choice(yandere)
                new_message = ' '.join(x.format(formatname)
                                       for x in new_message.split(' '))
                await bot.send_message(message.author, new_message)
            return

        message_channel = message.channel.name.lower()
        if reduce(
                lambda acc, n: acc or (n == message_channel),
                blacklist,
                False):
            return

        # spoopy factor
        if random.random() < 0.05:
            new_message = random.choice(yandere)
            new_message = ' '.join(x.format(message.author.mention)
                                   for x in new_message.split(' '))
            await bot.send_message(message.author, new_message)
            return

        # first let's have a tiny chance of snek actually responding with ooc content
        if random.random() <= 0.01:
            with open('./data/events/ooc/ooc.txt', 'r') as fobj:
                quotes = fobj.readlines()
            await bot.send_message(message.channel, random.choice(quotes))
            return

        # now lets check for contents

        clean_message = message.clean_content.lower()

        if 'praise' in clean_message or 'pray' in clean_message:
            root_dir = './data/events/pray'
            files_to_choose = [os.path.join(root_dir, f)
                               for f in os.listdir(root_dir)
                               if os.path.isfile(os.path.join(root_dir, f))]
            with open(random.choice(files_to_choose), 'rb') as fobj:
                new_msg = await bot.send_file(message.channel, fobj)
            await bot.add_reaction(new_msg, '🙏')
            return

        # only do the others half the time cause fuck it it's tooo much
        if random.random() <= 0.5:
            return

        if 'thank' in clean_message:
            new_message = "you're welcome"
            if random.random() < 0.5:
                new_message += " {}".format(message.author.mention)
            await bot.send_message(message.channel, new_message)

        elif 'zeb' in clean_message:
            new_message = await bot.send_message(message.channel, 'Daisuki, Zeb-kun!')
            await bot.add_reaction(new_message, '🐍')
            await bot.add_reaction(new_message, '🍆')
            await bot.add_reaction(new_message, '💦')

        elif 'snek' in clean_message:
            await bot.send_message(message.channel, ':snake: ~ !! I :black_heart: you senpai !! ~ :snake:')
        elif 'blood' in clean_message:
            await bot.send_message(message.channel, 'B̵̪̳̣͍̙̳̬̭͞͝L͢͏̸͏̧̙̼͓̘̯͉̩̩̞͚͕̲̰̼̘̦ͅÒ̮͈̖͔̰̞͝O̵͖͔̟̰͔͚̬͟͝ͅḐ̸̭͙̜̺̞͍͎͔͜͡͡ ̨̨̟̝̦̬̩̳̖͟ͅF̤̭̬͙̀̀͘͠O̶̯̠̞̲̫̱̻̮͎̦̳̝͉̮̕ͅŔ̡͈͕̼͖̥̰̭̟̝͟ ̡̲̯͉̤͈̘͎̬͎̺̟͞T̴̸̟̺̬̼̣̖͓̩̯͇̣̩̺̮͘Ḫ̣̥͍͙͍͓͔͈̖̬̘̩͔͖̝͖̀͘E̶̡̛̯̞̱̯̗͍͖͇̹̖̳̩̥̳̳̙͢͝ ̡͓͍͕͔̳̠͍̥̞̙͖̙̦͕̠̪̘̕ͅB̪͕̻̺͈̤̟̻͖̣͙̪̝̭̀͘͠Ḻ̵̨̞̯̥̭͈̪̻̰̭́́͝O̧͜͏̰͓̘̖̘̬̤ͅǪ̥̟̘̪̱͔͇̖͟D̸̡҉̶̫͕͖̹̤̜̪̟̝̯͚ ̵̨̛̯̺̤̮̲͓̦̜̪̕͝G̙̩͖̭̘̤̩̕Ǫ͎͉̲̤͓͇̦̖̯͇̥͔͓̣̘̦̪̀D͘͘͏͡͏͙̠͈̮̱̼')
        elif 'skull' in clean_message:
            await bot.send_message(message.channel, 'S̡̟͉̻͔̩͕͙̳͜͟͜K҉̵͏̳͕͉͈̟͙̰͖͍̦͙̱̙̥̤̞̱U͏̥̲͉̞͉̭͟͟ͅL̵̶̯̼̪͉̮̰͙͍͟͜Ḻ̶̗̬̬͉̗̖̮̰̹̺̬̺͢͢͡ͅͅŚ̶̢͎̳̯͚̠̞͉̦̙̥̟̲̺̗̮̱͚̬͡͠ ̶̡̧̲̟͖̤͓̮̮͕̭͍̟͔͓͚̺̣̱͙͍͜͜F̶̡̢̨̯͖͎̻̝̱͚̣̦̭̞̣̰̳̣̩O̴̴̷̠̜̥̭̳̩̤͎̦̲͈͝ͅŔ̡̨̼̝̩̣͙̬̱̫͉̭͈̗̙͢͡ ͠͏̗̙͎̫̟̜̻̹̹̘̬̖ͅT̴͉̙̥̲̠͎̭͇͚̟͝͡Ḩ̺͕̦̭̪̼̼̮̰͍̲͍̯̗͇͘͘͝͝E̡̻̮̘̭͎̥̺̘͉̟̪̮̮͜͢͡ ̡̰͙̮͙͈̠͍̞̠̀͠Ṣ̷̡̡̛̜̞̣͙͇̭̣̳͕̖̺̱̳̭͖͞ͅͅK̵҉̨͇̭̯͍̱̞̦͎̥̼͢U̡̧̯̗̙͇͈̣̪̲͜L̸̢͖͇̲̤̼͕͡L̻̻͖̭̪͖͙̫͎̜̲̬̕͜͞͡ͅ ̷̸̨̛̩͉̺̩͔̯͖̠̳͖̞̠̩͖̠ͅT̶̷̤̩͉̝̗̲͕̩̪̮̝̜̰̻̗̪̀ͅH̵̴̷̯̮͎̖͙̦̙͇̣̩̣̭̝́͝ͅR̨̧͍̮̪̜̯̖̹̜̹͈̗̕͡͠O҉̶͚͎̻͉̮̞͉̳ͅN̷̛̩̤̟̣͕͍͎̻̜͓̖̭͖̠͎̲̺͝ͅĘ̸̸͍̪̼̜͎̫̘̳͓̥')
        elif 'god' in clean_message:
            await bot.send_message(message.channel, 'P̸̨̛͖̦̮̘̯͙̭͍̣̠͕͜Ŕ̵̷̨̗̱͖̦̰͈͍̩̯̼͍̟̙͓̱̤͘ͅA̸̴̡͇̠͈͍̲͘͘ͅĮ̨͈͙̣̘̼́̕S̴̥̯̱̜̟͙̘̘͉̟̮̱̙̘̻͖͟͠͞E̢̨̘̮͕̺̖̰̹͢͝ ̷̴̡̛̗͈͓̻͔̭̫̝̦͎͙̳͙͓̠̞̪͔̱B̵̸̻̼̯̲̻͢͝E̱̘͇͔͙̯̥͉̪̱̤̪̩͍͉̲̟̖̗͜͢͢͜ ̨̡͕̮̤͉̙̦̱͚̬̖͈͢͞ͅÙ̳̫̙̰̙͓͘͘N̞̳͉̬͈̦̭̱̕̕͜T̶̳̝̼̗̝͡O̡̡͔̬͍͚͔̲̳͞ ̵̰͔̙̦̩͕͖̝N̡̡̬̗̣͔̗͔͖̳͚̠͙̤̙̼̘̞I̛̛̬̥̝̘̖̣̩G̵̕͝҉̖̮̩̼͓̯͙̳̀Ģ̵̹͇̙͔̼̼͎̞̤̬̜̭̣͙͕̳̻͘͡ͅǪ̴͕͈̮̮̩͔͎̼̫̝̼̹Ţ̸̧͚̬̣̪͉̲̪̖̹̻̪͚͉̟͚̥̹̀̕H̷͘҉̩͔̩̦̳̪̼̬͙̰̙͕̼͈ͅ ̸̯̤̠̙͓͇̣͙͓̗̙̜̞̯͜͞ͅŢ҉̵̯̥̩͖̬̺̻̮̘̼͔͍̞͈̼̲̪͜͟H̨͟҉̨̟̠̫̠̬̦̪̞͎͍͇̮͔ͅĘ̥̫͉̫͖̱͈̖̦̳̥͙̱͙̱͡ ̷̢̭̠͔̖̱W̟̩̪͍̘̩̦͟͟͞Ǫ̡͔̮̜̝̩̗̱̙͇̣̤̰̲̭̝̳̘̩́̀́ͅR̸̳̰̪̝͉̲̙̖̯̠̞̞̗͘͢M̴̨̭̦̗͖͎̬̳̖̲͢͡ ̨̛̙̰͕̦̠͚̠̖̘̲̱͜͡G̼̬̞̜̭͔̯̪̠̯̲̟̙̻̜̀͘͜O̡̖̰͕͙̯͖̙͍͙̲͈̘͓̥̱͢͢͠D̵̞̤̗͕̪͘͟͝͡ͅ')

        elif 'dragon' in clean_message:
            await bot.send_message(message.channel, dragonart)
        elif 'penis' in clean_message:
            root_dir = './data/events/penis'
            files_to_choose = [os.path.join(root_dir, f)
                               for f in os.listdir(root_dir)
                               if os.path.isfile(os.path.join(root_dir, f))]
            with open(random.choice(files_to_choose), 'rb') as fobj:
                new_msg = await bot.send_file(message.channel, fobj)
            await bot.add_reaction(new_msg, '🌈')
            await bot.add_reaction(new_msg, '🍆')
            await bot.add_reaction(new_msg, '💦')
        elif reduce(
                lambda acc, n: acc or (n in clean_message),
                dickwords,
                False):
            await bot.add_reaction(message, '🇵')
            await bot.add_reaction(message, '🇪')
            await bot.add_reaction(message, '🇳')
            await bot.add_reaction(message, '🇮')
            await bot.add_reaction(message, '🇸')
        elif reduce(
                lambda acc, n: acc or (n in clean_message),
                vag_words,
                False):
            await bot.add_reaction(message, '😞')

    n = Spoop(bot)
    bot.add_cog(n)
    bot.add_listener(message_events, 'on_message')

