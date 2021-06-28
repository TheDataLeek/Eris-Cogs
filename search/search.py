import os
from urllib import parse
from pprint import pprint as pp

from redbot.core import commands
import aiohttp
import wolframalpha

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

        term = parse.quote_plus(" ".join(term))
        search = self.wolfram_search_link.format(term)

        async with aiohttp.ClientSession() as session:
            async with session.get(search) as resp:
                data = await resp.json()
                links = []
                contents = data['queryresult']
                if contents['success'] == 'true':
                    if len(contents['pods']) > 0:
                        links.append(contents['pods'][0]['subpods'][0]['img']['src'])
                        links.append(contents['pods'][1]['subpods'][0]['img']['src'])
                if links:
                    await ctx.send('\n'.join(links))


if __name__ == '__main__':
    appid = os.environ['WOLFRAM']
    client = wolframalpha.Client(appid)
    res = client.query("current weather")
    print(next(res.results).text)
