import re
import json
import io
import csv
import discord
from redbot.core import commands, data_manager, Config, checks, bot
from redbot.core.utils import embed
import aiohttp
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

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
            cog_name="weather",
        )
        self._config.register_user(
            zip_code=None,
        )
        self._config.register_global(
            users_to_alert=list(),
        )

        data_dir = data_manager.bundled_data_path(self)
        zip_code_file = (data_dir / "zipcodes.csv").open(mode="r")
        csv_reader = csv.reader(zip_code_file)
        self.zip_codes = {
            row[0]: (row[1], row[2])
            for i, row in enumerate(csv_reader)
            if i != 0  # skip header
        }

        self.scheduler = AsyncIOScheduler(
            jobstores={"default": MemoryJobStore()},
        )
        for job in self.scheduler.get_jobs():
            job.remove()
        self.scheduler.start()

        async def get_weather_alerts():
            users = await self._config.users_to_alert()
            for userid in users:
                user = self.bot.get_user(userid)
                if user is None:
                    continue
                user_zip = await self._config.user(user).zip_code()
                if user_zip is None:
                    continue
                try:
                    lat, lon = self.zip_codes[user_zip]
                except KeyError:
                    continue
                try:
                    weather_metadata, forecast = await self.check_weather(lat, lon)
                except Exception as e:
                    print(e)
                    continue
                dm_channel: discord.DMChannel = user.dm_channel
                if dm_channel is None:
                    await user.create_dm()
                    dm_channel: discord.DMChannel = user.dm_channel

                alerts = []
                for period in forecast["properties"]["periods"][:3]:
                    if int(period["temperature"]) <= 15:  # fahrenheit
                        alerts.append(
                            f"# Freeze Alert!\n## {period['name']}\n{period['detailedForecast']}"
                        )
                    if int(period["temperature"]) >= 100:
                        alerts.append(
                            f"# Heat Alert!\n## {period['name']}\n{period['detailedForecast']}"
                        )
                    if "snow" in period["shortForecast"].lower():
                        alerts.append(
                            f"# Snow Alert!\n## {period['name']}\n{period['detailedForecast']}"
                        )
                    if int(period["windSpeed"].split(" ")[0]) >= 20:
                        alerts.append(
                            f"# Wind Alert!\n## {period['name']}\n{period['detailedForecast']}"
                        )
                alert_text = "\n".join(alerts)
                await dm_channel.send(alert_text)

        self.scheduler.add_job(
            get_weather_alerts, trigger=IntervalTrigger(minutes=60 * 4)
        )

    @commands.command()
    async def enable_weather_alerts(self, ctx: commands.Context):
        user: discord.User = ctx.author
        user_zip = await self._config.user(user).zip_code()
        if user_zip is None:
            await ctx.send(
                "You need to save your zipcode first! Please use [p]myzip to save!"
            )
            return
        users: list
        async with self._config.users_to_alert() as users:
            if user.id in users:
                await ctx.send("Weather alerts already enabled!")
            else:
                users.append(user.id)
                await ctx.send("Weather alerts enabled!")

    @commands.command()
    async def disable_weather_alerts(self, ctx: commands.Context):
        user: discord.User = ctx.author
        user_zip = await self._config.user(user).zip_code()
        if user_zip is None:
            await ctx.send(
                "You need to save your zipcode first! Please use [p]myzip to save!"
            )
            return

        users: list
        async with self._config.users_to_alert() as users:
            if user.id in users:
                users.remove(user.id)
                await ctx.send("Weather alerts disabled!")
            else:
                await ctx.send("Weather alerts already disabled!")

    @commands.command()
    async def weather(self, ctx: commands.Context, zipcode: str = None):
        """
        Get the weather for your saved zipcode, prompt to save zip if not saved
        """
        user: discord.User = ctx.author
        if zipcode is None:
            user_zip = await self._config.user(user).zip_code()
            if user_zip is None:
                await ctx.send(
                    "You need to save your zipcode first! Please use [p]myzip to save!"
                )
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

        try:
            weather_metadata, forecast = await self.check_weather(lat, lon)
        except Exception as e:
            await ctx.send(f"Unable to get weather! {e}")
            return

        forecast_periods = forecast["properties"]["periods"]
        forecast_lines = [
            f"**{period['name']}**\n{period['detailedForecast']}"
            for i, period in enumerate(forecast_periods)
            if i <= 4
        ]
        forecast_text = "\n".join(forecast_lines)
        city = weather_metadata["properties"]["relativeLocation"]["properties"]["city"]
        state = weather_metadata["properties"]["relativeLocation"]["properties"][
            "state"
        ]

        weblink = f"https://forecast.weather.gov/MapClick.php?lat={lat}&lon={lon}"
        embedded_response = discord.Embed(
            title=f"Weather Forecast for {city}, {state}",
            type="rich",
            description=forecast_text,
            url=weblink,
        )
        embedded_response.set_thumbnail(url=forecast_periods[0]["icon"])

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

    @commands.command()
    async def weatherdump(self, ctx: commands.Context, zipcode: str = None):
        user: discord.User = ctx.author
        if zipcode is None:
            user_zip = await self._config.user(user).zip_code()
            if user_zip is None:
                await ctx.send(
                    "You need to save your zipcode first! Please use [p]myzip to save!"
                )
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

        try:
            weather_metadata, forecast = await self.check_weather(lat, lon)
            weather_metadata, hourly_forecast = await self.check_weather(
                lat, lon, hourly=True
            )
        except Exception as e:
            await ctx.send(f"Unable to get weather! {e}")
            return

        full_forecast = {
            "forecast": forecast["properties"],
            "hourly": hourly_forecast["properties"],
        }
        buf = io.BytesIO()
        buf.write(json.dumps(full_forecast).encode())
        buf.seek(0)
        await ctx.send(file=discord.File(buf, filename="weather.json"))

    def check_zipcode(self, zipcode: str) -> bool:
        return bool(re.match(r"^\d{5}$", zipcode))

    async def check_weather(
        self, lat: str, lon: str, hourly: bool = False
    ) -> tuple[dict, dict]:
        async with aiohttp.ClientSession() as session:
            metadata_url = f"https://api.weather.gov/points/{lat},{lon}"
            async with session.get(metadata_url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Unable to get weather! STATUS {resp.status}")
                weather_metadata = await resp.json()

            forecast_url = weather_metadata["properties"]["forecast"]
            if hourly:
                forecast_url = weather_metadata["properties"]["forecastHourly"]

            async with session.get(forecast_url) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Unable to get weather! STATUS {resp.status}")
                forecast = await resp.json()

        return weather_metadata, forecast
