import io
import datetime as dt
import pprint
import discord
import random
from redbot.core import commands, bot, checks, data_manager, Config
from redbot.core.utils import embed

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
        self._config.register_guild(
            roulette_channels=list(),
            roulette_channel_info=dict(),
        )

    @commands.group()
    async def roulette(self, ctx: commands.Context):
        pass

    @roulette.command()
    @checks.mod()
    async def channels(self, ctx: commands.Context, *channels: discord.TextChannel):
        channel_ids = [c.id for c in channels]
        await self._config.guild(ctx.guild).roulette_channels.set(channel_ids)
        channel_info = {
            cid: {
                'last_fetched': None,
                'messages': list(),
            }
            for cid in channel_ids
        }
        await self._config.guild(ctx.guild).roulette_channel_info.set(channel_info)
        formatted = (
            f"{ctx.guild.name}\n"
            f"Channel IDs: {', '.join(channel_ids)}\n"
            f"Channel Info: {pprint.pformat(channel_info)}"
        )
        embedded_response = discord.Embed(
            title=f"Roulette Channels Set",
            type="rich",
            description=formatted,
        )
        embedded_response = embed.randomize_colour(embedded_response)

        await ctx.send(embed=embedded_response)

    @commands.command()
    async def hitme(self, ctx: commands.Context):
        original_message: discord.Message = ctx.message
        channel_list: list[int] = await self._config.guild(ctx.guild).roulette_channels()
        channel_to_use_id = random.choice(channel_list)

        async with self._config.guild(ctx.guild).roulette_channel_info() as roulette_channel_info:
            channel_info = roulette_channel_info[channel_to_use_id]
            channel_to_use: discord.TextChannel = await ctx.guild.fetch_channel(channel_to_use_id)

            if channel_info['last_fetched'] is None or (dt.datetime.now() - channel_info['last_fetched']) > dt.timedelta(days=7):
                media_messages: list[discord.Message] = await self.find_media_messages(channel_to_use)
                fetched_at = dt.datetime.now()
                message_ids = [m.id for m in media_messages]
                roulette_channel_info[channel_to_use_id]['last_fetched'] = fetched_at
                roulette_channel_info[channel_to_use_id]['messages'] = message_ids
            else:
                media_messages = [
                    await channel_to_use.fetch_message(cid)
                    for cid in channel_info['messages']
                ]

        media: list[discord.Attachment] = [
            attachment
            for message in media_messages
            for attachment in message.attachments
            if attachment.width
        ]

        media_to_use = random.choice(media)
        extension = media_to_use.filename.split('.')[-1]
        buf = io.BytesIO()
        await media_to_use.save(buf)
        buf.seek(0)
        await ctx.send(
            reference=original_message,
            file=discord.File(buf, filename=f'roulette.{extension}', spoiler=True)
        )

    async def find_media_messages(self, channel: discord.TextChannel) -> list[discord.Message]:
        # let's start with just the latest 500
        media_messages: list[discord.Messaeg] = []
        message: discord.Message = None
        last_message_examined: discord.Message = None
        while True:
            chunk = [message async for message in channel.history(limit=1000, before=last_message_examined)]
            if len(chunk) == 0:
                break
            for message in chunk:
                if len(message.attachments) and any(a.width for a in message.attachments):
                    media_messages.append(message)
            last_message_examined = message

        return media_messages
