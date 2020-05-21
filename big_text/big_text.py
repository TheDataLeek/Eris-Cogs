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
            return

        match_check = re.match("[A-Za-z ]", raw_msg.lower())
        if bool(match_check):
            clean_msg = raw_msg.lower()

            big_msg = ""
            for letter in clean_msg:
                to_append = ""
                if bool(re.match("[A-Za-z]", letter)):
                    big_msg += (":regional_indicator_%s:" % letter)
                elif bool(re.match("[ ]", letter)):
                    big_msg += " "

            await ctx.send(big_msg)