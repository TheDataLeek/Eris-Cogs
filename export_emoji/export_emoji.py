# stdlib
import io
import zipfile
from zipfile import ZipFile

from typing import Union

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class ExportEmoji(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def export(self, ctx, *emoji: Union[discord.PartialEmoji, discord.Emoji]):
        """
        Insult the user.
        Usage: [p]insult <Member>
        Example: [p]insult @Eris#0001
        """
        if len(emoji) == 0:
            await ctx.send("No emoji to download!")
            return

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            for e in emoji:
                asset = e.url
                url = str(asset)
                name = f"{e.name}.gif"
                new_buf = io.BytesIO()
                await asset.save(new_buf)
                zf.writestr(name, new_buf.getvalue())

        buf.seek(0)

        await ctx.send(
            file=discord.File(buf, filename='export.zip')
        )








