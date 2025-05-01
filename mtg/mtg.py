# stdlib
import io
import re
import time
import aiohttp
import random
import string
import json

# third party
import discord
from redbot.core import commands, data_manager, Config, checks, Config
from thefuzz import process


BaseCog = getattr(commands, "Cog", object)

COLORS = {
    "W": "#E1E4C7",
    "R": "#EBA689",
    "U": "#A7DEFC",
    "B": "#C2C1BF",
    "G": "#A1D0B0",
}


class MTG(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot

        self.bot.add_listener(self.pull_card_references, "on_message")
        self.bot.add_listener(self.pull_card_embed, "on_message")

        data_dir = data_manager.bundled_data_path(self)
        # datafile from here https://mtgjson.com/downloads/all-files/
        # only includes the names tho, need to clean up on each new set release
        raw_cards = (data_dir / "cards.csv").read_text().lower()
        allowed_chars = string.ascii_lowercase + " \n\r"
        raw_cards = "".join(char for char in raw_cards if (char in allowed_chars))
        self.all_cards = list(set(raw_cards.splitlines()))

    async def pull_card_references(self, message: discord.Message):
        ctx: commands.Context = await self.bot.get_context(message)
        text = message.clean_content.lower()
        matches = re.findall(r"\[\[(.+?)\]\]", text, re.IGNORECASE)
        if not matches:
            return

        cards = []
        async with aiohttp.ClientSession(
            headers={"User-Agent": "ErisMTGDiscordBot/1.0", "Accept": "*/*"}
        ) as session:
            for match in matches:
                try:
                    cards += await query_scryfall(session, match, self.all_cards)
                except Exception as e:
                    print(e)

        channel: discord.TextChannel = ctx.channel
        await channel.send(files=cards)

    async def pull_card_embed(self, message: discord.Message):
        ctx: commands.Context = await self.bot.get_context(message)
        text = message.clean_content.lower()
        matches = re.findall(r"\{\{(.+?)\}\}", text, re.IGNORECASE)
        if not matches:
            return

        cards = []
        async with aiohttp.ClientSession(
            headers={"User-Agent": "ErisMTGDiscordBot/1.0", "Accept": "*/*"}
        ) as session:
            for match in matches:
                try:
                    cards += await query_scryfall(
                        session, match, self.all_cards, datatype="json"
                    )
                except Exception as e:
                    print(e)

        channel: discord.TextChannel = ctx.channel

        for card in cards:
            description = (
                f"{card['oracle_text']}\n-\n"
                f"Legal in Commander? {card['legalities']['commander']}\n"
                f"Price: ${card['prices']['usd']}\n"
                f"[Scryfall]({card['scryfall_uri']})\n"
                f"[TCG Player]({card['purchase_uris']['tcgplayer']})"
            )
            card_embed = discord.Embed(
                title=f"{card['name']} - {card['mana_cost']}",
                type="rich",
                description=description,
                color=discord.Color.from_str(COLORS[card["colors"][0]]),
            )
            card_embed.set_thumbnail(url=card["image_uris"]["png"])
            await channel.send(embed=card_embed)

    @commands.command()
    async def decklist_to_json(self, ctx: commands.context):
        message: discord.Message = ctx.message
        message_contents: str = message.content
        decklist = message_contents.splitlines()
        cards = []
        async with aiohttp.ClientSession(
            headers={"User-Agent": "ErisMTGDiscordBot/1.0", "Accept": "*/*"}
        ) as session:
            for line in decklist:
                if line[0] not in (string.ascii_letters + string.digits):
                    continue

                try:
                    referenced_card = await query_scryfall(
                        session, line, self.all_cards, datatype="json"
                    )
                    referenced_card = [
                        {
                            key: value
                            for key, value in card_face.items()
                            if key in ("name", "oracle_text", "mana_cost")
                        }
                        for card_face in referenced_card
                    ]
                    cards += referenced_card
                except Exception as e:
                    print(e)

        channel: discord.TextChannel = ctx.channel
        json_decklist = json.dumps(cards, indent=2)
        buf = io.BytesIO()
        buf.write(json_decklist.encode("utf-8"))
        buf.seek(0)
        await channel.send(files=[discord.File(buf, filename="decklist.json")])

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
    session: aiohttp.ClientSession,
    card_name: str,
    all_cards: list[str],
    datatype="image",
) -> list[io.BytesIO] | list[dict]:
    card_exists = (
        any(card.startswith(card_name.lower()) for card in all_cards)
        or any(card_name.lower() in card for card in all_cards)
        or (card_name.lower() in all_cards)
    )
    if not card_exists:
        card_name, score = process.extractOne(card_name, all_cards)

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
