import discord
from redbot.core import commands, checks
import random
import re

BaseCog = getattr(commands, "Cog", object)

holiday_prefixes = list(
    {
        "Abominable",
        "Angelic",
        "Anticipating",
        "Aunt",
        "Blessed",
        "Candlelit",
        "Cheerful",
        "Cheery",
        "Childlike",
        "Chilly",
        "Cozy",
        "Crackling",
        "Crisp",
        "Crystalline",
        "Drunk",
        "Enchanted",
        "Excited",
        "Exhausted",
        "Festive",
        "Fireside",
        "Frigid",
        "Frostbitten",
        "Frosty",
        "Frozen",
        "Generous",
        "Gift-Wrapped",
        "Gingerbread",
        "Glacial",
        "Glistening",
        "Grandma",
        "Grandpa",
        "Happy",
        "Heavenly",
        "Holy",
        "Homemade",
        "Hypothermic",
        "Icy",
        "Jingling",
        "Jolly",
        "Joyful",
        "Lavish",
        "Little",
        "Mead-Soaked",
        "Melting",
        "Merry",
        "Mirthful",
        "Naughty",
        "Nice",
        "Nippy",
        "Ornamental",
        "Pine-Scented",
        "Roasted",
        "Santa",
        "Secret",
        "Shivering",
        "Snowbound",
        "Snowy",
        "Sparkling",
        "Special",
        "Spiced",
        "Spiked",
        "Sugar-Coated",
        "Surprise",
        "Sweet",
        "Thankful",
        "Thoughtful",
        "Tickle Me",
        "Toasty",
        "Tranquil",
        "Twinkling",
        "Uncle", 
        "Wintry",
        "Wondrous",
        "Wrapped",
        "Yuletide",
        "Yummy",
        "Zesty"
    }
)

holiday_suffixes = list(
    {
        "In a Box",
        "the Elf",
        "Claus",
        "Themed Socks",
        "the Snowman",
        "On the Shelf",
        "The Red-Nosed Reindeer",
        "Incarnate"
    }
)
holiday_names = list(
    {
        "Elsa",
        "Mrs. Claus",
        "Ebenezer Scrooge",
        "Santa's Little Helper",
        "Krampus",
        "Rudolph",
        "Buddy"
    }
)


class Boo(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    def prefix_nick(self, nick, wordlist):
        return random.choice(wordlist) + " " + nick

    def suffix_nick(self, nick, wordlist):
        return nick + " " + random.choice(wordlist)

    def replace_nick(self, nick, wordlist):
        return random.choice(wordlist)

    def random_alter(self, nick):
        alteration = list({"SUFFIX", "PREFIX", "REPLACE"})
        weights = list({2,15,1})
        choice = random.choices(alteration, weights=weights, k=1)
        if choice == "PREFIX":
            return self.prefix_nick(nick, wordlist=holiday_prefixes)
        if choice == "SUFFIX":
            return self.suffix_nick(nick, wordlist=holiday_suffixes)
        if choice == "REPLACE":
            return self.replace_nick(nick, wordlist=holiday_names)

    async def update_username(self, ctx):
        user = ctx.message.author

        original_nick = user.nick or user.display_name

        new_nick = self.random_alter(original_nick)

        if len(new_nick) >= 32 or len(new_nick.split(" ")) > 3:
            base_nick = new_nick.split(" ")[-1]
            new_nick = self.random_alter(base_nick)

        new_nick = new_nick.title()

        try:
            await user.edit(nick=new_nick)
        except Exception as e:
            print(e)
            await ctx.send(user.mention + " -> " + new_nick)

    @commands.command()
    async def jolly(self, ctx):
        await self.update_username(ctx)