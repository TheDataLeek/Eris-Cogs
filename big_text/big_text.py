import string
import random
from redbot.core import commands


BaseCog = getattr(commands, "Cog", object)


class BigText(BaseCog):
    max_message_length = 20
    variant_chance = 90
    loud_emojis = [":hyperblob:",
                   ":rainbowhype:"]
    letter_variants = {"a": ":a:",
                       "b": ":b:",
                       "i": ":information_source:",
                       "m": ":m:",
                       "o": ":o2:",
                       "x": ":x:"}

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def big_text(self, ctx):
        raw_msg = await self.get_raw_msg(ctx)

        if self.length_is_ok(ctx, raw_msg):
            big_msg = await self.msg_to_emoji(ctx, raw_msg, True)
            if big_msg != "":
                await ctx.send(big_msg)
        else:
            await ctx.send(f"Message must be {self.max_message_length} characters or shorter!")

    """
    Converts a raw string message to block letter emoji with optional variants
    In addition - adds loud emojis to either side of the message
    """
    @commands.command()
    async def loud_text(self, ctx):
        raw_msg = await self.get_raw_msg(ctx)
        loud_emoji = random.choice(self.loud_emojis)
        if self.length_is_ok(ctx, raw_msg):
            loud_msg = await self.msg_to_emoji(ctx, raw_msg, True)
            if loud_msg != "":
                loud_msg = loud_emoji + loud_msg + loud_emoji
                await ctx.send(loud_msg)
        else:
            await ctx.send(f"Message must be {self.max_message_length} characters or shorter!")

    """ 
    Limits users to short, mostly readable exclamations.
    This also sets the max final message length to 440 characters unless a function adds extra decorative emojis
    (22 per emoji * 20)
    """
    def length_is_ok(self, ctx, raw_msg):
        if len(raw_msg) >= self.max_message_length:
            return False
        else:
            return True

    """
    Converts a raw string message to block letter emoji with optional variants and sends to channel
    """
    async def msg_to_emoji(self, ctx, raw_msg, use_variants):
        big_msg = ""
        if raw_msg == "":
            return raw_msg

        for letter in raw_msg.lower():
            if letter in string.ascii_lowercase:
                if use_variants and letter in self.letter_variants.keys() and random.random() > self.variant_chance:
                    big_msg += self.letter_variants.get(letter)
                else:
                    big_msg += f":regional_indicator_{letter}:"
            elif letter == " ":
                big_msg += " "
            else:
                await ctx.send("Message can only have A-Z characters, numbers and spaces")
                return ""
        return big_msg

    async def get_raw_msg(self, ctx):
        raw_msg = " ".join(ctx.message.clean_content.split(" ")[1:])
        if raw_msg == "":
            await ctx.send("Message cannot be empty!")
            return ""
        else:
            return raw_msg
