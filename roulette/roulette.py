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
        channel_ids = [str(c.id) for c in channels]
        formatted = (
            f"{ctx.guild.name}\n"
            f"Channel IDs: {', '.join(channel_ids)}\n"
        )
        embedded_response = discord.Embed(
            title=f"Roulette Channels Set",
            type="rich",
            description=formatted,
        )
        embedded_response = embed.randomize_colour(embedded_response)

        await ctx.send(embed=embedded_response)

        await self._config.guild(ctx.guild).roulette_channels.set(channel_ids)

    @commands.command()
    async def hitme(self, ctx: commands.Context):
        original_message: discord.Message = ctx.message
        channel_list: list[str] = await self._config.guild(ctx.guild).roulette_channels()
        current_channel: discord.Message = ctx.channel
        current_channel_id = str(current_channel.id)
        if current_channel_id in channel_list:
            return

        channel_to_use_id = random.choice(channel_list)
        channel_to_use: discord.TextChannel = await ctx.guild.fetch_channel(int(channel_to_use_id))

        first_day_in_channel: dt.date = await self.find_first_message(channel_to_use)
        today = dt.date.today()
        time_since: dt.timedelta = (today - first_day_in_channel)
        days_since = time_since.days
        random_day = (first_day_in_channel + dt.timedelta(days=random.randint(0, days_since)))
        media = await self.find_media_from_day(channel_to_use, random_day)
        media_to_use = random.choice(media)
        extension = media_to_use.filename.split('.')[-1]
        buf = io.BytesIO()
        await media_to_use.save(buf)
        buf.seek(0)
        await ctx.send(
            reference=original_message,
            file=discord.File(buf, filename=f'roulette.{extension}', spoiler=True)
        )

    async def find_first_message(self, channel: discord.TextChannel) -> dt.datetime:
        first_timestamps = []
        async for message in channel.history(limit=5, oldest_first=True):
            first_timestamps.append(message.created_at.date())
        return min(first_timestamps)

    async def find_media_from_day(self, channel: discord.TextChannel, day: dt.date) -> list[discord.Attachment]:
        media: list[discord.Attachment] = []
        chunk = [message async for message in channel.history(limit=100, around=dt.datetime(day.year, day.month, day.day))]
        for message in chunk:
            for attachment in message.attachments:
                if attachment.width:
                    media.append(attachment)
        return media
