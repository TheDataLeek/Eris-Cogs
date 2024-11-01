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
        self.bot.add_listener(self.pull_card_embed, "on_message")

    async def pull_card_references(self, message: discord.Message):
        ctx: commands.Context = await self.bot.get_context(message)
        text = message.clean_content.lower()
        matches = re.findall(r"\[\[(.+?)\]\]", text, re.IGNORECASE)
        if not matches:
            return

        cards = []
        async with aiohttp.ClientSession(headers={"User-Agent": "ErisMTGDiscordBot/1.0", "Accept": "*/*"}) as session:
            for match in matches:
                cards += await query_scryfall(session, match)

        channel: discord.TextChannel = ctx.channel
        await channel.send(files=cards)

    async def pull_card_embed(self, message: discord.Message):
        ctx: commands.Context = await self.bot.get_context(message)
        text = message.clean_content.lower()
        matches = re.findall(r"\{\{(.+?)\}\}", text, re.IGNORECASE)
        if not matches:
            return

        cards = []
        async with aiohttp.ClientSession(headers={"User-Agent": "ErisMTGDiscordBot/1.0", "Accept": "*/*"}) as session:
            for match in matches:
                cards += await query_scryfall(session, match, datatype="json")

        channel: discord.TextChannel = ctx.channel

        for card in cards:
            card_embed = discord.Embed(
                title=f"{card['name']} - {card['mana_cost']}", type="rich", description=card["oracle_text"]
            )
            card_embed.set_thumbnail(url=card["image_uris"]["png"])
            card_embed.set_footer(text=card["scryfall_uri"])
            await channel.send(embed=card_embed)

    @commands.command()
    async def send_targets(self, ctx: commands.context, *users: discord.Member):
        users: list[discord.Member] = [*users]
        random.shuffle(users)
        for i, user in enumerate(users):
            channel: discord.DMChannel = user.dm_channel
            if channel is None:
                channel = await user.create_dm()

            if i == len(users) - 1:
                target_index = 0
            else:
                target_index = i + 1

            target: discord.Member = users[target_index]
            name = target.display_name
            base_name = target.name

            await channel.send(f"Your target is {name} (@{base_name})")


async def query_scryfall(
    session: aiohttp.ClientSession, card_name: str, datatype="image"
) -> list[io.BytesIO] | list[dict]:
    data = []
    url = "https://api.scryfall.com/cards/named"
    for i in range(2):
        if datatype == "image":
            fetch_url = f"{url}?format=image&version=png&fuzzy={card_name}"
            if i == 1:
                fetch_url = f"{fetch_url}&face=back"
        else:
            fetch_url = f"{url}?format=json&fuzzy={card_name}"
            if i == 1:
                break
        async with session.get(fetch_url) as resp:
            if resp.status != 200:
                continue
            if datatype == "image":
                cardbuf = io.BytesIO()
                cardbuf.write(await resp.read())
                cardbuf.seek(0)
                data.append(discord.File(cardbuf, filename=f"{card_name}.png"))
            else:
                data.append(await resp.json())
        time.sleep(0.1)
    return data
