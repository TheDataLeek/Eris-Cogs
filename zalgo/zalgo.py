import discord
from redbot.core import commands
import random
import re

BaseCog = getattr(commands, "Cog", object)


class Zalgo(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def zalgo(self, ctx):
        """Zalgo the text"""
        # first pull out the .zalgo part of the message
        raw_msg = " ".join(ctx.message.clean_content.split(" ")[1:])
        if raw_msg == "":
            raw_msg = "HE COMES"

        # random intensity
        intensity = random.randint(50, 150)

        # zalgo characters to fuck with
        zalgo_chrs = [chr(x) for x in range(0x0300, 0x036F + 1)]
        zalgo_chrs += [u"\u0488", u"\u0489"]

        msg_array = list(raw_msg)
        for i in range(intensity):
            index = random.randint(0, len(msg_array) - 1)
            msg_array.insert(index, random.choice(zalgo_chrs))

        zalgo_msg = "".join(msg_array)

        await ctx.message.delete()
        await ctx.send(zalgo_msg)

    @commands.command()
    async def uwu(self, ctx):
        """uwu the text"""
        # first pull out the .zalgo part of the message
        raw_msg = " ".join(ctx.message.content.split(" ")[1:])
        if raw_msg == "":
            raw_msg = "uwu"

        replacements = {
            "r": "w",
            "R": "W",
            "l": "w",
            "L": "W",
            "this": "dis",
            "This": "Dis",
            "they": "dey",
            "They": "Dey",
            "there": "dere",
            "There": "Dere",
            "the": "da",
            "The": "Da",
        }

        new_msg = raw_msg
        for regex, replacement in replacements.items():
            new_msg, _ = re.subn(regex, replacement, new_msg)

        await ctx.message.delete()
        await ctx.send(new_msg)
