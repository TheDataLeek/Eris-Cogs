# stdlib
import datetime
import pytz
from dateutil import tz
from typing import Optional, Dict
from pprint import pprint as pp

# third party
import discord
from redbot.core import commands, bot, Config
from redbot.core.utils import embed
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from fuzzywuzzy import process
import aiohttp

BaseCog = getattr(commands, "Cog", object)


class Timezone(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot: bot = bot_instance
        self.timezones = pytz.all_timezones

        self.config = Config.get_conf(
            self,
            identifier=890910101201298734756,
            force_registration=True,
            cog_name="tz",
        )

        default_global = {"default_timezone": {}}
        self.config.register_global(**default_global)

        self.tzapisettings: Dict[str, str] = {}
        self.token: str = ""

        self.fmt = "%H:%M:%S %Z%z"

    async def get_token(self):
        self.tzapisettings = await self.bot.get_shared_api_tokens("timezone")
        self.token = self.tzapisettings.get("token", None)

    @commands.group()
    async def tz(self, ctx: commands.Context):
        """Group for timezone/ip info"""
        pass

    @tz.command()
    async def list(self, ctx: commands.Context):
        """
        List all available timezones
        """
        formatted = "\n".join(pytz.all_timezones)
        pages = list(pagify(formatted, page_length=300))
        await menu(ctx, pages, DEFAULT_CONTROLS)

    @tz.command()
    async def help(self, ctx: commands.Context):
        """
        Get help on the timezoneapi token configuration
        """
        msg = (
            "In order to get IP lookups working, you'll need to enable the timezone API\n"
            "1. Go to TimezoneAPI here https://timezoneapi.io/developers\n"
            "2. Sign up for a free account (15k credits / month)\n"
            "3. In your email you'll get a token.\n"
            "4. You can now set that token IN A DM WITH THE BOT via `.set api timezone token <your token here>`"
        )

        embedded_response = discord.Embed(
            title=f"API Signup Info",
            type="rich",
            description=msg,
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)

    def get_timezone_from_string(self, timezone: str) -> Optional[str]:
        if timezone not in self.timezones:
            timezone, score = process.extractOne(timezone, list(self.timezones))
            if score <= 0.5:
                return None
        return timezone

    @tz.command()
    async def default(self, ctx: commands.Context, *timezone: str):
        """
        Sets your default timezone
        """
        timezone = " ".join(timezone)
        timezone = self.get_timezone_from_string(timezone)
        if timezone is None:
            await ctx.send("Error, can't find timezone!")
            return

        async with self.config.default_timezone() as defaults:
            defaults[str(ctx.author.id)] = timezone

        await ctx.send(
            f"Success, {ctx.author.display_name}'s default timezone is now {timezone}"
        )

    @tz.command()
    async def to(
        self, ctx: commands.Context, timezone: str, from_timezone: Optional[str] = None
    ):
        timezone = self.get_timezone_from_string(timezone)
        if timezone is None:
            await ctx.send("Error, can't find timezone!")
            return

        if from_timezone is None:
            async with self.config.default_timezone() as defaults:
                if str(ctx.author.id) not in defaults:
                    await ctx.send("No default set, need to provide origin timezone")
                else:
                    from_timezone = defaults[str(ctx.author.id)]
        else:
            from_timezone = self.get_timezone_from_string(from_timezone)
            if from_timezone is None:
                await ctx.send("Error, I can't find your specified origin timezone")

        # set origin timezone
        origin = pytz.timezone('UTC')
        now = datetime.datetime.utcnow()
        origin = origin.localize(now)   # utc localized

        origin = origin.astimezone(pytz.timezone(from_timezone))  # actual

        result = origin.astimezone(pytz.timezone(timezone))  # converted

        embedded_response = discord.Embed(
            title=f"Converting {from_timezone} to {timezone}",
            type="rich",
            description=f"It's currently {origin.strftime(self.fmt)} which is equal to {result.strftime(self.fmt)}",
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)

    @tz.command()
    async def ip(self, ctx: commands.Context, ip: str):
        await self.get_token()
        if self.token is None:
            await ctx.send("Need to set timezoneapi token first!")
            return


if __name__ == "__main__":
    origin = pytz.timezone('UTC')
    now = datetime.datetime.utcnow()
    origin = origin.localize(now)
    print(origin)   # utc localized

    origin = origin.astimezone(pytz.timezone("America/Denver"))
    print(origin)

    to_timezone = pytz.timezone("America/Los_Angeles")
    print(origin.astimezone(to_timezone))
