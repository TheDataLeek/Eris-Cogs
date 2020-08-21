import string

from redbot.core import commands
import re

BaseCog = getattr(commands, "Cog", object)


class BigText(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def big_text(self, ctx):
        raw_msg = " ".join(ctx.message.clean_content.split(" ")[1:])
        if raw_msg == "":
            await ctx.send("Message cannot be empty!")
            return

        """ 
        Limits users to short, mostly readable exclamations.
        This also sets the max final message length to 440 characters (22 per emoji * 20)
        """
        if len(raw_msg) >= 20:
            await ctx.send("Message must 20 characters or shorter!")
            return

        big_msg = ""
        for letter in raw_msg.lower():
            if letter in string.ascii_lowercase:
                big_msg += f":regional_indicator_{letter}:"
            elif letter == " ":
                big_msg += " "
            else:
                await ctx.send("Message can only have A-Z characters and spaces")
                return

        await ctx.send(big_msg)
