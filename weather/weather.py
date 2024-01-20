import re
import json
import csv
import discord
from redbot.core import commands, data_manager, Config, checks, bot
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
    async def weather(self, ctx: commands.Context):
        """
        Get the weather for your saved zipcode, prompt to save zip if not saved
        """
        user: discord.User = ctx.author
        user_zip = await self._config.user(user).zip_code()
        await ctx.send(f"Your zipcode is `{user_zip}`")
        if user_zip is None:
            await ctx.send("You need to save your zipcode first! Please use [p]myzip to save!")
            return

        try:
            lat, lon = self.zip_codes[user_zip]
        except KeyError:
            await ctx.send(f"Unable to find your zipcode {user_zip}!")
            return

        await ctx.send(f"Your lat/lon is `{lat}`, `{lon}`")

        async with aiohttp.ClientSession() as session:
            metadata_url = f"https://api.weather.gov/points/{lat},{lon}"
            await ctx.send(metadata_url)
            async with session.get(metadata_url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Unable to get weather! STATUS {resp.status}")
                    return
                weather_metadata = await resp.json()

            await ctx.send(f"""```\n{json.dumps(weather_metadata)}\n```""")

            forecast_url = weather_metadata['properties']['forecast']

            await ctx.send(forecast_url)

            async with session.get(forecast_url) as resp:
                if resp.status != 200:
                    await ctx.send(f"Unable to get weather! STATUS {resp.status}")
                    # return
                forecast = await resp.json()
                await ctx.send(f"""```\n{json.dumps(forecast)}\n```""")

    @commands.command()
    async def myzip(self, ctx: commands.Context, zipcode: str):
        """
        User command to save your zipcode for weather lookups
        """
        if not re.match(r"^\d{5}$", zipcode):
            await ctx.send(f"Invalid zipcode {zipcode}!")
            return
        await self._config.user(ctx.author).zip_code.set(zipcode)
