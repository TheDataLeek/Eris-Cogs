# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class Insult(BaseCog):
    """Insult Cog"""

    def __init__(self, bot):
        self.bot = bot
        data_dir = data_manager.bundled_data_path(self)
        insults = (data_dir / "insults.txt").read_text().split("\n")
        self.insults = insults

    @commands.command()
    async def insult(self, ctx, user: discord.Member = None):
        """
        Insult the user.
        Usage: [p]insult <Member>
        Example: .insult @Eris#0001
        """
        msg = " "
        if user is None:
            await ctx.send(ctx.message.author.mention + msg + randchoice(self.insults))
        else:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = (
                    " How original. No one else had thought of trying to get the bot to insult "
                    "itself. I applaud your creativity. Yawn. Perhaps this is why you don't have "
                    "friends. You don't add anything new to any conversation. You are more of a "
                    "bot than me, predictable answers, and absolutely dull to have an actual conversation with."
                )
                await ctx.send(user.mention + msg)
            else:
                async with ctx.typing():
                    sleep(1)
                    if random.random() <= 0.5:
                        msg = " {}".format(randchoice(self.insults))
                        await ctx.send(user.mention + msg)
                    else:
                        url = "https://evilinsult.com/generate_insult.php?lang=en&type=text"
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as resp:
                                insult = await resp.text()
                                await ctx.send("{} {}".format(user.mention, insult))
