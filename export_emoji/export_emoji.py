# stdlib
import io
import zipfile
from zipfile import ZipFile

from typing import Union, Tuple

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class ExportEmoji(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def export(self, ctx, *emoji: Union[discord.PartialEmoji, discord.Emoji, int, str]):
        """
        Export emoji to zipfile.

        Can provide either a list of emoji or the message id of the message with emoji in it or reacted to it.
        String emoji cannot be exported
        """
        if len(emoji) == 0:
            await ctx.send("No emoji to download!")
            return

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for e in emoji:
                if isinstance(e, discord.PartialEmoji) or isinstance(e, discord.Emoji):
                    name, new_buf = await self._export_emoji(e)
                    zf.writestr(name, new_buf.getvalue())
                elif isinstance(e, int):
                    # if int, assume message id
                    message: discord.Message = await ctx.message.channel.fetch_message(e)
                    reactions = message.reactions
                    for r in reactions:
                        react_emoji = r.emoji
                        if not isinstance(react_emoji, str):
                            name, new_buf = await self._export_emoji(react_emoji)
                            zf.writestr(name, new_buf.getvalue())

        buf.seek(0)

        await ctx.send(file=discord.File(buf, filename="export.zip"))


    async def _export_emoji(self, emoji: Union[discord.Emoji, discord.PartialEmoji]) -> Tuple[str, io.BytesIO]:
        asset = emoji.url
        url = str(asset)
        suffix = 'png'
        if emoji.animated:
            suffix = 'gif'
        name = f"{emoji.name}.{suffix}"
        new_buf = io.BytesIO()
        await asset.save(new_buf)
        return name, new_buf
