import pathlib
import json
import hashlib

import openai
import bs4
import aiohttp
from async_lru import alru_cache
from markdownify import markdownify as md

CACHE = pathlib.Path(__file__).parent / "pages"


class URLContent:
    name: str
    content: str
    markdown: str
    hex: str
    soup: bs4.BeautifulSoup
    summary: str = None

    def __init__(self, url: str):
        self.url: str = url

    @alru_cache(maxsize=128)
    async def fetch(self):
        async with aiohttp.ClientSession() as session:
            resp: aiohttp.ClientResponse
            async with session.get(self.url) as resp:
                if resp.status != 200:
                    return

                self.content = await resp.text()
                self.soup = bs4.BeautifulSoup(self.content, "html.parser")
                self.markdown = md(self.content)
                self.name = self.soup.title.string
                self.hex = hashlib.sha256(self.url.encode("utf-8")).hexdigest()

    async def to_dict(self):
        if self.content is None:
            await self.fetch()

        return {
            "url": self.url,
            "hex": self.hex,
            "name": self.name,
            "content": self.content,
            "markdown": self.markdown,
            "summary": self.summary,
        }

    @classmethod
    def from_json(cls, data: dict | pathlib.Path) -> "URLContent":
        if isinstance(data, pathlib.Path):
            data = json.loads(data.read_text())
        content = cls(data["url"])
        content.hex = data["hex"]
        content.content = data["content"]
        content.markdown = data["markdown"]
        content.name = data.get("name")
        content.summary = data.get("summary")
        return content

    def format_for_openai(self) -> dict:
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "".join(
                        [
                            "---\n",
                            f"NAME OF PAGE: {self.name}\n",
                            f"SUMMARY: {self.summary}\n",
                            f"CONTENTS:\n{self.markdown}\n",
                            "---\n",
                        ]
                    ),
                },
            ],
        }


class ContentStore:
    def __init__(self, cache_dir: pathlib.Path = CACHE):
        self.cache_dir = cache_dir
        self.contents: dict[str, URLContent] = {}

    async def add(self, content: URLContent):
        self.contents[content.url] = content
        await self.save()

    async def save(self):
        for _, content in self.contents.items():
            json_content = json.dumps(await content.to_dict())
            (self.cache_dir / f"{content.hex}.json").write_text(json_content)

    def load(self):
        for file in CACHE.glob("*.json"):
            content = URLContent.from_json(file)
            self.contents[content.url] = content

    async def fetch_content(self, url: str) -> URLContent:
        if url in self.contents:
            return self.contents[url]
        else:
            content = URLContent(url)
            await content.fetch()
            await self.add(content)
            return content

    def to_dict(self) -> dict:
        return {url: content.to_dict() for url, content in self.contents.items()}

    def to_openai(self) -> list[dict]:
        return [content.format_for_openai() for _, content in self.contents.items()]
