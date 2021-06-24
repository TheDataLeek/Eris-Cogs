# stdlib
import io
from zipfile import ZipFile

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class ExportEmoji(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def export(self, ctx, *emoji: discord.Emoji):
        """
        Insult the user.
        Usage: [p]insult <Member>
        Example: [p]insult @Eris#0001
        """
        if len(emoji) == 0:
            await ctx.send("No emoji to download!")
            return

        urls = [e.url for e in emoji]
        data = []
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url) as resp:
                    img = await resp.read()
                    data.append(img)

        await ctx.send(urls)





