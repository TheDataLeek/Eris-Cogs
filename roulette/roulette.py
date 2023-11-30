import io

import discord
import random
from redbot.core import commands, bot, checks, data_manager, Config

BaseCog = getattr(commands, "Cog", object)


class Roulette(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance
        self._config = Config.get_conf(
            self,
            identifier=234898972371739000001,
            force_registration=True,
            cog_name='roulette'
        )
        self._config.register_guild(channels={})

    @commands.group()
    async def roulette(self, ctx: commands.Context):
        pass

    @roulette.command()
    @checks.mod()
    async def channels(self, ctx: commands.Context, *channels: discord.TextChannel):
        await self._config.guild(ctx.guild).channels.set(set(channels))

    @commands.command()
    async def hitme(self, ctx: commands.Context):
        original_message: discord.Message = ctx.message
        channel_list: set[discord.TextChannel] = await self._config.guild(ctx.guild).channels()
        channel_to_use = random.choice(list(channel_list))
        media: list[discord.Attachment] = await self.find_media(channel_to_use)
        media_to_use = random.choice(media)
        extension = media_to_use.filename.split('.')[-1]
        buf = io.BytesIO()
        await media_to_use.save(buf)
        buf.seek(0)
        await ctx.send(
            reference=original_message,
            file=discord.File(buf, filename=f'roulette.{extension}', spoiler=True)
        )

    async def find_media(self, channel: discord.TextChannel) -> list[discord.Attachment]:
        # let's start with just the latest 500
        media: list[discord.Attachment] = []
        message: discord.Message = None
        last_message_examined: discord.Message = None
        while True:
            chunk = [message async for message in channel.history(limit=1000, before=last_message_examined)]
            if len(chunk) == 0:
                break
            for message in chunk:
                media += [
                    attachment
                    for attachment in message.attachments
                    if attachment.width
                ]
            last_message_examined = message

        return media
