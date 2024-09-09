# stdlib
import io
import re
import time
import aiohttp
import random

# third party
import discord
from redbot.core import commands, data_manager, Config, checks, Config


BaseCog = getattr(commands, "Cog", object)


class MTG(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot

        self.bot.add_listener(self.pull_card_references, "on_message")

    async def pull_card_references(self, message: discord.Message):
        ctx: commands.Context = await self.bot.get_context(message)
        text = message.clean_content.lower()
        matches = re.findall(r"\[\[(.+?)\]\]", text, re.IGNORECASE)
        if not matches:
            return

        cards = []
        async with aiohttp.ClientSession(headers={"User-Agent": "ErisMTGDiscordBot/1.0", "Accept": "*/*"}) as session:
            url = "https://api.scryfall.com/cards/named"
            for match in matches:
                async with session.get(f"{url}?format=image&version=png&fuzzy={match}") as resp:
                    if resp.status != 200:
                        continue
                    cardbuf = io.BytesIO()
                    cardbuf.write(await resp.read())
                    cardbuf.seek(0)
                    cards.append(discord.File(cardbuf, filename=f"{match}.png"))

                time.sleep(0.1)

        channel: discord.TextChannel = ctx.channel
        await channel.send(files=cards)

    @commands.command()
    async def send_targets(self, ctx: commands.context, *users: discord.Member):
        users: list[discord.Member] = [*users]
        random.shuffle(users)
        for i, user in enumerate(users):
            channel: discord.DMChannel = user.dm_channel
            if channel is None:
                channel = await user.create_dm()

            if i == len(users) - 1:
                i = 0

            target: discord.Member = users[i]
            name = target.display_name
            base_name = target.name

            await channel.send(f"Your target is {name} (@{base_name})")
