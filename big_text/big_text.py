from redbot.core import commands
import re

BaseCog = getattr(commands, "Cog", object)


class BigText(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def big_text(self, ctx):
        raw_msg = " ".join(ctx.message.clean_content.split(" ")[1:])
        if raw_msg is "":
            await ctx.send("Message cannot be empty!")

        match_check = re.match("[A-Za-z ]", raw_msg.lower())
        if bool(match_check):

            big_msg = ""
            for letter in raw_msg.lower():
                if bool(re.match("[a-z]", letter)):
                    big_msg += (":regional_indicator_%s:" % letter)
                elif bool(re.match("[ ]", letter)):
                    big_msg += " "

            await ctx.send(big_msg)
        else:
            await ctx.send("Message can only have A-Z characters and spaces")
