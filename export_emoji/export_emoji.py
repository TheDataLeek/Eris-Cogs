# stdlib
import io
import os
import pathlib
import datetime as dt
import re
import time
import zipfile
from typing import Union, Tuple, List, Optional

# third party
import discord
from redbot.core import commands, data_manager, checks
from redbot.core.bot import Red

BaseCog = getattr(commands, "Cog", object)

# https://github.com/Rapptz/discord.py/blob/master/discord/partial_emoji.py#L95
# Thanks @TrustyJaid!!
_CUSTOM_EMOJI_RE = re.compile(
    r"<?(?P<animated>a)?:?(?P<name>[A-Za-z0-9\_]+):(?P<id>[0-9]{13,20})>?"
)


class ExportEmoji(BaseCog):
    def __init__(self, bot):
        self.bot: Red = bot
        self.data_path: pathlib.Path = data_manager.cog_data_path(self)

    @commands.command()
    @checks.is_mod_or_superior
    async def create_archive(self, ctx):
        channel: discord.TextChannel = ctx.channel
        messages = []
        images = []
        last_message_examined: discord.Message = None
        stime = time.time()
        zipbuf = io.BytesIO()
        total_count = 0
        chunksize = 1000
        with zipfile.ZipFile(zipbuf, "w", zipfile.ZIP_DEFLATED) as zf:
            while True:
                counter = 0
                message: discord.Message
                async for message in channel.history(limit=chunksize, oldest_first=True, after=last_message_examined):
                    author: discord.Member = message.author

                    attachment_buffers = []
                    attachment: discord.Attachment
                    for attachment in message.attachments:
                        if attachment.height and attachment.width:
                            buf = io.BytesIO()
                            await attachment.save(buf)
                            attachment_buffers.append((attachment.filename, message.created_at, buf))
                    images += attachment_buffers

                    messages.append([message.created_at, author.display_name, message.clean_content])
                    counter += 1

                total_count += counter

                # if we got very few messages, break!
                if counter <= 5:
                    break

                # snag the last message examined
                last_message_examined = message

            # write the messages to the zipfile
            created_at: dt.datetime
            name: str
            content: str
            messages = [
                f"{created_at.isoformat()} | {name} | {content if content else '<attachment>'}"
                for created_at, name, content in messages
            ]
            messages = '\n\n'.join(messages)
            zf.writestr('log.txt', messages)

            # write the attachments
            filename: str
            created_at: str
            buffer: io.BytesIO
            for filename, created_at, buffer in images:
                formatted_filename = f"{created_at.isoformat()}_{filename}"
                zf.writestr(formatted_filename, buffer.getvalue())

        zipbuf.seek(0)

        delta = time.time() - stime
        minutes = delta // 60
        seconds = delta - (minutes * 60)

        await ctx.send(
            f"Done. Found {total_count:,} messages and {len(images):,} images. "
            f"Duration of {minutes:0.0f} minutes, {seconds:0.03f} seconds"
        )
        try:
            await ctx.send(
                file=discord.File(zipbuf, filename=f"archive.zip")
            )
        except Exception as e:
            await ctx.send("Too much data! Here's the text log. "
                           "Contact the bot owner for the zipfile (saved to data directory")
            buf = io.BytesIO()
            buf.write(messages.encode('utf-8'))
            buf.seek(0)
            await ctx.send(
                file=discord.File(buf, filename=f"log.txt")
            )

            archive_dir = self.data_path / 'archives'
            if not archive_dir.exists():
                os.mkdir(archive_dir)
            filepath = archive_dir / f"channel_archive_{dt.datetime.now().isoformat()}.zip"
            zipbuf.seek(0)
            filepath.write_bytes(zipbuf.getvalue())
            filepath = str(filepath.absolute())
            jump_url = ctx.message.jump_url
            await self.bot.send_to_owners(f'Archive saved to the data directory!\n{filepath}\n{jump_url}')


    @commands.command()
    async def export(
        self, ctx, *emoji_list: Union[discord.PartialEmoji, discord.Emoji, int, str]
    ):
        """
        Export emoji to zipfile.

        Can provide either a list of emoji or the message id of the message with emoji in it or reacted to it.
        String emoji cannot be exported
        """
        message: discord.Message = ctx.message

        zipbuf = io.BytesIO()
        count = 0
        with zipfile.ZipFile(zipbuf, "w") as zf:
            for emoji_to_export in emoji_list:
                if isinstance(emoji_to_export, discord.PartialEmoji) or isinstance(
                    emoji_to_export, discord.Emoji
                ):
                    name, buf = await self._export_emoji(emoji_to_export)
                    zf.writestr(name, buf.getvalue())
                    count += 1
                elif isinstance(emoji_to_export, int):
                    # if int, assume message id
                    message: discord.Message = await ctx.message.channel.fetch_message(
                        emoji_to_export
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

        zipbuf.seek(0)

        if count == 0:
            await ctx.send("Nothing to download or export!")
            return

        await ctx.send(
            file=discord.File(zipbuf, filename=f"export_of_{count:0.0f}.zip")
        )

    async def _export_emoji(
        self, emoji: Union[discord.Emoji, discord.PartialEmoji]
    ) -> Tuple[str, io.BytesIO]:
        asset: discord.Asset = emoji.url
        url = str(asset)
        suffix = "png"
        if emoji.animated:
            suffix = "gif"
        name = f"{emoji.name}.{suffix}"
        new_buf = io.BytesIO()
        num_bytes: int = await asset.save(new_buf)
        return name, new_buf

    async def _export_sticker(self, sticker: discord.Sticker) -> Tuple[str, io.BytesIO]:
        asset: Optional[discord.Asset] = sticker.image_url
        if asset:
            name = f"{sticker.name}.png"
            new_buf = io.BytesIO()
            num_bytes: int = await asset.save(new_buf)
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

        # currently does not work for some reason...
        for sticker in message.stickers:
            name, new_buf = await self._export_sticker(sticker)
            results.append((name, new_buf))

        substrings: List[str] = _CUSTOM_EMOJI_RE.findall(message.content)
        # taken from https://github.com/Rapptz/discord.py/blob/master/discord/partial_emoji.py#L95
        # waiting for discord.py 2.0
        for animated, name, emoji_id in substrings:
            state = message._state
            emoji = discord.PartialEmoji.with_state(
                state, name=name, animated=animated, id=emoji_id
            )
            # await ctx.send(emoji)
            name, new_buf = await self._export_emoji(emoji)
            results.append((name, new_buf))

        return results
