# stdlib
import io
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

        data = [
            {
                'asset': e.url,
                'url': str(e.url),
                'name': e.name,
                'data': None
            }
            for e in emoji
        ]
        for obj in data:
            asset: discord.Asset = obj['asset']
            buf = io.BytesIO()
            await asset.save(buf)
            obj['data'] = buf
            await ctx.send(
                file=discord.File(obj['data'], filename=obj['name'])
            )






