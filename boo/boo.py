import discord
from redbot.core import commands
import random
import re


BaseCog = getattr(commands, "Cog", object)


prefixes = [
    'Afraid',
    'Apparition',
    'Bat',
    'Bloodcurdling',
    'Bloody',
    'Bones',
    'Broomstick',
    'Cackle',
    'Cadaver',
    'Carved',
    'Casket',
    'Cauldron',
    'Cemetery',
    'Cobweb',
    'Coffin',
    'Corpse',
    'Creepy',
    'Decapitated',
    'Decomposing',
    'Eerie',
    'Fangs',
    'Frightening',
    'Ghost',
    'Ghoulish',
    'Goblin',
    'Gory',
    'Grim Reaper',
    'Gruesome',
    'Haunted',
    'Horrifying',
    'Howling',
    'Jack - O - Lantern',
    'Lurking',
    'Macabre',
    'Magic',
    'Mausoleum',
    'Morbid',
    'Mummy',
    'Occult',
    'Owl',
    'Petrified',
    'Phantom',
    'Poltergeist',
    'Scary',
    'Scream',
    'Shadow',
    'Skeleton',
    'Skull',
    'Specter',
    'Spell',
    'Spider',
    'Spirit',
    'Superstition',
    'Tomb',
    'Trick or treat',
    'Undead',
    'Unearthly',
    'Unnerving',
    'Vampire',
    'Warlock',
    'Werewolf',
    'Witch',
    'Wizard',
    'Wraith',
    'Zombie',
]


class Boo(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def boo(self, ctx, user: discord.Member=None):
        if user is None:  # or user.id == '142431859148718080':
            user = ctx.message.author

        new_nick = random.choice(prefixes) + ' ' + user.nick
        if len(new_nick) > 32:
            new_nick = random.choice(prefixes) + user.nick.split(' ')[:-1]

        try:
            await user.edit(nick=new_nick)
        except:
            await ctx.send(new_nick)
