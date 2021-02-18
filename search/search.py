from redbot.core import commands
from urllib import parse
import aiohttp

BaseCog = getattr(commands, "Cog", object)


class Search(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.search_link = "https://en.wikipedia.org/w/api.php?action=opensearch&search={}&limit=1&namespace=0&format=json"

    @commands.command()
    async def wiki(self, ctx, *term: str):
        new_term = parse.quote_plus(" ".join(term))
        search = self.search_link.format(new_term)

        async with aiohttp.ClientSession() as session:
            async with session.get(search) as resp:
                data = await resp.json()
                if len(data) == 0:
                    await ctx.send("No pages found!")
                    return
                await ctx.send(data[-1][0])
