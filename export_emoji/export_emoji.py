# stdlib
import io
import zipfile
from zipfile import ZipFile

from typing import Union, Tuple, List

# third party
import discord
from redbot.core import commands, data_manager
import aiohttp


BaseCog = getattr(commands, "Cog", object)


class ExportEmoji(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def export(
        self, ctx, *emoji: Union[discord.PartialEmoji, discord.Emoji, int, str]
    ):
        """
        Export emoji to zipfile.

        Can provide either a list of emoji or the message id of the message with emoji in it or reacted to it.
        String emoji cannot be exported
        """
        message: discord.Message = ctx.message

        buf = io.BytesIO()
        count = 0
        with zipfile.ZipFile(buf, "w") as zf:
            for e in emoji:
                if isinstance(e, discord.PartialEmoji) or isinstance(e, discord.Emoji):
                    name, new_buf = await self._export_emoji(e)
                    zf.writestr(name, new_buf.getvalue())
                    count += 1
                elif isinstance(e, int):
                    # if int, assume message id
                    message: discord.Message = await ctx.message.channel.fetch_message(
                        e
                    )
                    buf_list = await self._export_from_message(message)
                    for name, buf in buf_list:
                        zf.writestr(name, buf.getvalue())
                        count += 1

            if message.reference:
                message_id = message.reference.message_id
                referenced_message = await ctx.message.channel.fetch_message(message_id)
                buf_list = await self._export_from_message(referenced_message)
                for name, buf in buf_list:
                    zf.writestr(name, buf.getvalue())
                    count += 1

        buf.seek(0)

        if count == 0:
            await ctx.send("No emoji to download!")
            return

        await ctx.send(file=discord.File(buf, filename=f"export_of_{count:0.0f}.zip"))

    async def _export_emoji(
        self, emoji: Union[discord.Emoji, discord.PartialEmoji]
    ) -> Tuple[str, io.BytesIO]:
        asset = emoji.url
        url = str(asset)
        suffix = "png"
        if emoji.animated:
            suffix = "gif"
        name = f"{emoji.name}.{suffix}"
        new_buf = io.BytesIO()
        await asset.save(new_buf)
        return name, new_buf

    async def _export_from_message(
        self, message: discord.Message
    ) -> List[Tuple[str, io.BytesIO]]:
        reactions = message.reactions
        results = []
        for r in reactions:
            react_emoji = r.emoji
            if not isinstance(react_emoji, str):
                name, new_buf = await self._export_emoji(react_emoji)
                results.append((name, new_buf))

        return results
