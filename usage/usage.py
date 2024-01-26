import io
import json
import discord
from redbot.core import commands, data_manager, Config, checks
from redbot.core.bot import Red

from typing import Union


BaseCog = getattr(commands, "Cog", object)


class Usage(BaseCog):
    def __init__(self, bot_instance: Red):
        self.bot = bot_instance
        self._config = Config.get_conf(
            self,
            identifier=101004765642020101,
            force_registration=True,
            cog_name="usage",
        )
        self._config.register_global(
            dm_log=list(),
            command_log=list(),
        )

        self.bot.add_listener(self.usage_message_handler, "on_message")

    async def get_prefix(self, message: discord.message) -> list[str]:
        prefix = await self.bot.get_prefix(message)
        if not isinstance(prefix, list):
            prefix = [prefix]
        return prefix

    async def usage_message_handler(self, message: discord.Message):
        prefixes = await self.get_prefix(message)
        bot_command = False
        for prefix in prefixes:
            bot_command |= message.content.startswith(prefix)

        if bot_command:
            guild: Union[str, int] = "DM" if message.guild is None else message.guild.id
            async with self._config.command_log() as command_log:
                command_log.append(
                    {
                        "timestamp": f"{message.created_at.isoformat()}",
                        "guild": guild,
                        "author": message.author.id,
                        "channel": message.channel.id,
                        "command": message.content.split(" ")[0],
                        "content": message.clean_content,
                    }
                )

        bot_dm = message.guild is None and isinstance(
            message.channel, discord.DMChannel
        )
        if bot_dm:
            async with self._config.dm_log() as dm_log:
                dm_log.append(
                    {
                        "timestamp": f"{message.created_at.isoformat()}",
                        "author": message.author.id,
                        "content": message.clean_content,
                        "attachments": [
                            attachment.url for attachment in message.attachments
                        ],
                    }
                )

    @commands.command()
    @checks.is_owner()
    async def show_usage(self, ctx: commands.Context):
        if not isinstance(ctx.channel, discord.DMChannel):
            return

        dm_log = await self._config.dm_log()
        command_log = await self._config.command_log()

        dm_log_buffer = io.BytesIO()
        dm_log_buffer.write(json.dumps(dm_log, indent=2).encode())
        dm_log_buffer.seek(0)
        await ctx.send(file=discord.File(dm_log_buffer, filename=f"dms.json"))

        command_log_buffer = io.BytesIO()
        command_log_buffer.write(json.dumps(command_log, indent=2).encode())
        command_log_buffer.seek(0)
        await ctx.send(file=discord.File(command_log_buffer, filename=f"commands.json"))

    @commands.command(aliases=["bug", "bugreport", "bug_report", "tell_owner"])
    async def hey(self, ctx: commands.Context):
        """
        Send a message to the bot owner!
        """
        message = ctx.message
        message_content = " ".join(message.clean_content.split(" ")[1:])
        attachments = []
        for attachment in message.attachments:
            buf = io.BytesIO()
            await attachment.save(buf)
            buf.seek(0)
            attachments.append([buf, attachment.filename])

        app_info: discord.AppInfo = await self.bot.application_info()
        owner: discord.User = app_info.owner

        dm_channel: discord.DMChannel = owner.dm_channel
        if dm_channel is None:
            dm_channel = await owner.create_dm()

        source_channel = "DM" if message.guild is None else message.channel.mention

        await dm_channel.send(
            f"Message from {message.author.name}\n{source_channel}\n{message_content}",
            files=[
                discord.File(buffer, filename=filename)
                for buffer, filename in attachments
            ],
        )

        await ctx.send(f"Message sent to {owner.name}!")
