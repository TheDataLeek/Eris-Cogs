import discord
from redbot.core import commands
import random
import re
from functools import reduce

BaseCog = getattr(commands, "Cog", object)


class Zalgo(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        async def april_fools(message):
            # Prevent acting on DM's
            if (
                random.random() <= 0.999
                or (message.guild is None)
                or message.guild.name.lower() != "cortex"
            ):
                return

            clean_message = message.clean_content.lower()
            # MM: Added so list instead of string
            message_split = clean_message.split(" ")
            # BLACKLIST CHANNELS
            blacklist = [
                "news",
                "rpg",
                "events",
                "recommends",
                "politisophy",
                "eyebleach",
                "weeb-lyfe",
                "out-of-context",
                "jokes",
                "anime-club",
            ]

            message_channel = message.channel.name.lower()

            if (
                # DO NOT RESPOND TO SELF MESSAGES
                (bot.user.id == message.author.id or message.content.startswith("."))
                or (message.channel.name is None)
                or (
                    reduce(
                        lambda acc, n: acc or (n == message_channel), blacklist, False
                    )
                )
                or ("thank" in clean_message)
                or ("http" in clean_message)
            ):
                return

            ctx = await bot.get_context(message)

            new_msg = self.uwuify(message.content)

            await ctx.message.delete()
            await ctx.send(new_msg)

        self.bot.add_listener(april_fools, "on_message")

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

    def uwuify(self, msg):
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

        new_msg = msg
        for regex, replacement in replacements.items():
            new_msg, _ = re.subn(regex, replacement, new_msg)

        new_msg += " *uwu*"

        return new_msg

    @commands.command()
    async def uwu(self, ctx):
        """uwu the text"""
        # first pull out the .zalgo part of the message
        raw_msg = " ".join(ctx.message.content.split(" ")[1:])
        if raw_msg == "":
            raw_msg = "uwu"

        new_msg = self.uwuify(raw_msg)

        await ctx.message.delete()
        await ctx.send(new_msg)

    @commands.command()
    async def spoilerify(self, ctx, *msg):
        new_msg = ''
        do_it = False
        for c in ' '.join(msg):
            if c != ' ' and do_it:
                new_msg += f'||{c}||'
                do_it = not do_it
            else:
                new_msg += c

        await ctx.message.delete()
        await ctx.send(new_msg)
