import re
import json
import csv
import discord
from redbot.core import commands, data_manager, Config, checks, bot
from redbot.core.utils import embed
import aiohttp

BaseCog = getattr(commands, "Cog", object)
RETYPE = type(re.compile("a"))


class Weather(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance
        self._config = Config.get_conf(
            self,
            identifier=3245786348567891999,
            force_registration=True,
            cog_name='weather',
        )
        self._config.register_user(
            zip_code=None,
        )

        data_dir = data_manager.bundled_data_path(self)
        zip_code_file = (data_dir / "zipcodes.csv").open(mode='r')
        csv_reader = csv.reader(zip_code_file)
        self.zip_codes = {
            row[0]: (row[1], row[2])
            for i, row in enumerate(csv_reader)
            if i != 0  # skip header
        }

    @commands.command()
    async def weather(self, ctx: commands.Context, zipcode: str = None):
        """
        Get the weather for your saved zipcode, prompt to save zip if not saved
        """
        if zipcode is None:
            user: discord.User = ctx.author
            user_zip = await self._config.user(user).zip_code()
            if user_zip is None:
                await ctx.send("You need to save your zipcode first! Please use [p]myzip to save!")
                return
        elif not self.check_zipcode(zipcode):
            await ctx.send(f"Invalid zipcode {zipcode}!")
            return
        else:
            user_zip = zipcode

        try:
            lat, lon = self.zip_codes[user_zip]
        except KeyError:
            await ctx.send(f"Unable to find your zipcode {user_zip}!")
            return

        async with aiohttp.ClientSession() as session:
            metadata_url = f"https://api.weather.gov/points/{lat},{lon}"
            async with session.get(metadata_url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Unable to get weather! STATUS {resp.status}")
                    return
                weather_metadata = await resp.json()

            forecast_url = weather_metadata['properties']['forecast']

            async with session.get(forecast_url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Unable to get weather! STATUS {resp.status}")
                    return
                forecast = await resp.json()

        forecast_periods = forecast['properties']['periods']
        forecast_lines = [
            f"*{period['name']}*\n{period['detailedForecast']}"
            for period in forecast_periods
        ]
        forecast_text = "\n".join(forecast_lines)
        city = weather_metadata['properties']['relativeLocation']['properties']['city']
        state = weather_metadata['properties']['relativeLocation']['properties']['state']

        weblink = f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}"
        embedded_response = discord.Embed(
            title=f"Weather Forecast for {city}, {state}",
            type="rich",
            description=forecast_text,
            url=weblink
        )
        embedded_response.set_thumbnail(url=forecast_periods[0]['icon'])

        embedded_response.set_footer(
            text="Forecast provided by NWS & NOAA",
            icon_url="https://www.noaa.gov/sites/default/files/styles/landscape_width_1275/public/2022-11/NOAAlogoWhiteBG16x9.jpg"
        )

        await ctx.send(embed=embedded_response)

    @commands.command()
    async def myzip(self, ctx: commands.Context, zipcode: str):
        """
        User command to save your zipcode for weather lookups
        """
        if not self.check_zipcode(zipcode):
            await ctx.send(f"Invalid zipcode {zipcode}!")
            return
        await self._config.user(ctx.author).zip_code.set(zipcode)
        await ctx.send("Zipcode saved!")

    def check_zipcode(self, zipcode: str) -> bool:
        return bool(re.match(r"^\d{5}$", zipcode))
