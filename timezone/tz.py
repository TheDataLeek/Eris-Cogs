# stdlib
from typing import Optional, Dict

# third party
import discord
from redbot.core import commands, bot, Config
from redbot.core.utils import embed

from fuzzywuzzy import process
import aiohttp

BaseCog = getattr(commands, "Cog", object)


class Timezone(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot: bot = bot_instance
        self.timezones = {
            "HST": -10,
            "Hawaii Standard Time": -10,
            "HDT": -9,
            "Hawaii-Aleutian Daylight Time": -9,
            "AKDT": -8,
            "Alaska Daylight Time": -8,
            "PDT": -7,
            "Pacific Daylight Time": -7,
            "MST": -7,
            "Mountain Standard Time": -7,
            "MDT": -6,
            "Mountain Daylight Time": -6,
            "CDT": -5,
            "Central Daylight Time": -5,
            "EDT": -4,
            "Eastern Daylight Time": -4,
        }

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

    async def get_token(self):
        self.tzapisettings = await self.bot.get_shared_api_tokens("timezone")
        self.token = self.tzapisettings.get("token", None)

    @commands.group()
    def tz(self):
        """Group for timezone info"""
        pass

    @tz.command()
    def help(self, ctx: commands.Context):
        """
        Get help on the timezoneapi token configuration
        """
        msg = (
            "In order to get IP lookups working, you'll need to enable the timezone API\n"
            "1. Go to TimezoneAPI here https://timezoneapi.io/developers\n"
            "2. Sign up for a free account (15k credits / month)\n"
            "3. In your email you'll get a token.\n"
            "4. You can now set that token IN A DM WITH THE BOT via `.set api timezone token <your token here>"
        )

        embedded_response = discord.Embed(
            title=f"API Signup Info",
            type="rich",
            description=msg,
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)

    def get_timezone_from_string(self, timezone):
        if timezone not in self.timezones:
            timezone, score = process.extractOne(timezone, list(self.timezones.keys()))
            if score <= 0.5:
                return None
        return timezone

    @tz.command()
    def default(self, ctx: commands.Context, timezone: str):
        """
        Sets your default timezone
        """
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
    def to(
        self, ctx: commands.Context, timezone: str, from_timezone: Optional[str] = None
    ):
        timezone = self.get_timezone_from_string(timezone)
        if timezone is None:
            await ctx.send("Error, can't find timezone!")
            return

    @tz.command()
    def iplookup(self, ctx: commands.Context, ip: str):
        self.get_token()
        if self.token is None:
            await ctx.send("Need to set timezoneapi token first!")
            return


if __name__ == "__main__":
    pass
