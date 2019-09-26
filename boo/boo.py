import discord
from redbot.core import commands
import random
import re

BaseCog = getattr(commands, "Cog", object)

prefixes = list(
    {'Afraid', 'Apparition', 'Bat', 'Bloodcurdling', 'Bloody', 'Bones', 'Broomstick', 'Cackle', 'Cadaver', 'Carved',
     'Casket', 'Cauldron', 'Cemetery', 'Cobweb', 'Coffin', 'Corpse', 'Creepy', 'Decapitated', 'Decomposing', 'Eerie',
     'Fangs', 'Frightening', 'Ghost', 'Ghoulish', 'Goblin', 'Gory', 'Grim Reaper', 'Gruesome', 'Haunted', 'Horrifying',
     'Howling', 'Jack - O - Lantern', 'Lurking', 'Macabre', 'Magic', 'Mausoleum', 'Morbid', 'Mummy', 'Occult', 'Owl',
     'Petrified', 'Phantom', 'Poltergeist', 'Scary', 'Scream', 'Shadow', 'Skeleton', 'Skull', 'Specter', 'Spell',
     'Spider', 'Spirit', 'Superstition', 'Tomb', 'Trick or treat', 'Undead', 'Unearthly', 'Unnerving', 'Vampire',
     'Warlock', 'Werewolf', 'Witch', 'Wizard', 'Wraith', 'Zombie', 'Afraid', 'Afterlife', 'Alarming', 'Alien', 'Angel',
     'Apparition', 'Astronaut', 'Autumn', 'Ballerina', 'Bat', 'Beast', 'Bizarre', 'Black', 'Black cat', 'Blood',
     'Bloodcurdling', 'Bogeyman', 'Bone', 'Boo', 'Broomstick', 'Cackle', 'Cadaver', 'Candy', 'Cape', 'Carve', 'Casket',
     'Cat', 'Cauldron', 'Cemetery', 'Chilling', 'Cloak', 'Clown', 'Cobweb', 'Coffin', 'Corpse', 'Costume', 'Cowboy',
     'Cowgirl', 'Creepy', 'Crown', 'Crypt', 'Dark', 'Darkness', 'Dead', 'Death', 'Demon', 'Devil', 'Devilish',
     'Disguise', 'Dreadful', 'Dress-up', 'Eerie', 'Elf', 'Enchant', 'Evil', 'Eyeballs', 'Eyepatch', 'Face paint',
     'Fairy', 'Fall', 'Fangs', 'Fantasy', 'Fear', 'Firefighter', 'Flashlight', 'Fog', 'Fright', 'Frighten',
     'Frightening', 'Frightful', 'Genie', 'Ghastly', 'Ghost', 'Ghostly', 'Ghoul', 'Ghoulish', 'Goblin', 'Goodies',
     'Gory', 'Gown', 'Grave', 'Gravestone', 'Grim', 'Grim Reaper', 'Grisly', 'Gruesome', 'Hair-raising', 'Halloween',
     'Hat', 'Haunt', 'Haunted house', 'Hayride', 'Headstone', 'Hobgoblin', 'Hocus pocus', 'Horrible', 'Horrify', 'Howl',
     'Imp', 'Jack-o\'-lantern', 'Jumpsuit', 'Kimono', 'King', 'Lantern', 'Macabre', 'Magic', 'Magic wand',
     'Make-believe', 'Make-up', 'Mask', 'Masquerade', 'Mausoleum', 'Midnight', 'Mist', 'Monster', 'Moon', 'Moonlight',
     'Moonlit', 'Morbid', 'Mummy', 'Mysterious', 'Night', 'Nightmare', 'Ninja', 'October', 'Ogre', 'Orange',
     'Otherworldly', 'Owl', 'Party', 'Petrify', 'Phantasm', 'Phantom', 'Pirate', 'Pitchfork', 'Poltergeist', 'Potion',
     'Prank', 'Pretend', 'Prince', 'Princess', 'Pumpkin', 'Queen', 'Repulsive', 'Revolting', 'Robe', 'Robot', 'Scare',
     'Scarecrow', 'Scary', 'Scream', 'Shadow', 'Shadowy', 'Shock', 'Shocking', 'Skeleton', 'Skull', 'Soldier',
     'Specter', 'Spell', 'Spider', 'Spider web', 'Spine-chilling', 'Spirit', 'Spook', 'Spooky', 'Startling', 'Strange',
     'Superhero', 'Supernatural', 'Superstition', 'Sweets', 'Tarantula', 'Terrible', 'Terrify', 'Thirty-first',
     'Thrilling', 'Tiara', 'Toga', 'Tomb', 'Tombstone', 'Treat', 'Treats', 'Trick', 'Trick-or-treat', 'Troll', 'Tutu',
     'Unearthly', 'Unnerving', 'Vampire', 'Vanish', 'Wand', 'Warlock', 'Web', 'Weird', 'Werewolf', 'Wicked', 'Wig',
     'Witch', 'Witchcraft', 'Wizard', 'Wizardry', 'Wraith', 'Zombie'})


class Boo(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def boo(self, ctx, user: discord.Member = None):
        if user is None:  # or user.id == '142431859148718080':
            user = ctx.message.author

        original_nick = user.nick or user.display_name

        new_nick = random.choice(prefixes) + ' ' + original_nick
        while len(new_nick) >= 32:
            parts = original_nick.split(' ')
            to_remove = random.choice(parts)
            parts.remove(to_remove)
            new_nick = random.choice(prefixes) + ' ' + ' '.join(parts)

        try:
            await user.edit(nick=new_nick)
        except Exception as e:
            print(e)
            await ctx.send(new_nick)
