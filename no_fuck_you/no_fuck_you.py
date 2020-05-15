import re
import discord
from redbot.core import commands, data_manager, Config, checks, bot


BaseCog = getattr(commands, "Cog", object)

RETYPE = type(re.compile('a'))


class NoFuckYou(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

        self.event_config = self.bot.get_cog('EventConfig')
        if self.event_config is None:
            raise FileNotFoundError('Need to install event_config')

        self.fuck_you_regex: RETYPE = re.compile("((f[uck]{1,3}) ([you]{1,3}))", flags=re.IGNORECASE)

        self.bot.add_listener(self.no_fuck_you, "on_message")

    async def no_fuck_you(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        allowed: bool = await self.event_config.allowed(ctx, message)
        keyword_in_message: bool = bool(self.fuck_you_regex.search(message.clean_content))

        if not allowed or not keyword_in_message:
            return

        await ctx.send("No fuck you")

        await self.event_config.log_last_message(ctx, message)

