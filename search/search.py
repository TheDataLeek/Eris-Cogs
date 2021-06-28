import io
import os
from urllib import parse
from pprint import pprint as pp
import json

from redbot.core import commands
import discord
import aiohttp

BaseCog = getattr(commands, "Cog", object)


class Search(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.wiki_search_link = "https://en.wikipedia.org/w/api.php?action=opensearch&search={}&limit=1&namespace=0&format=json"
        self.wolfram_search_link = "https://api.wolframalpha.com/v2/query?appid={}&input={}&format=image&output=json"

    @commands.command()
    async def wiki(self, ctx, *term: str):
        """
        Search wikipedia for provided search term, and return the first result.
        """
        new_term = parse.quote_plus(" ".join(term))
        search = self.wiki_search_link.format(new_term)

        async with aiohttp.ClientSession() as session:
            async with session.get(search) as resp:
                data = await resp.json()
                try:
                    contents = data[-1][0]
                except IndexError:
                    await ctx.send("No pages found!")
                    return
                await ctx.send(contents)

    async def get_wolfram_token(self):
        self.wolframsettings = await self.bot.get_shared_api_tokens("wolfram")
        self.wolfram_token = self.wolframsettings.get("appid", None)
        return self.wolfram_token

    @commands.command()
    async def wolfram(self, ctx, *term: str):
        """
        Search Wolfram Alpha
        """
        appid = await self.get_wolfram_token()
        if appid is None:
            await ctx.send('No token set!')
            return

        new_term = parse.quote(" ".join(term))
        search = self.wolfram_search_link.format(appid, new_term)

        async with aiohttp.ClientSession() as session:
            async with session.get(search) as resp:
                data = await resp.text()
                data = json.loads(data)
                links = []
                contents = data['queryresult']
                if contents['success']:
                    for pod in contents['pods']:
                        for subpod in pod['subpods']:
                            links.append(subpod['img']['src'])
            if links:
                imgs = []
                for i, link in enumerate(links[:10]):
                    async with session.get(link) as resp:
                        imgs.append(discord.File(io.BytesIO(await resp.read()), filename=f"{i}.gif"))

                await ctx.send(
                    files=imgs
                )
            else:
                await ctx.send('Request not understood!')

