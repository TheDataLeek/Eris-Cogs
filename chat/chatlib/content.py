import pathlib
import json
import hashlib

import openai
import bs4
import aiohttp
from async_lru import alru_cache
from markdownify import markdownify as md

from . import model_querying

CACHE = pathlib.Path(__file__).parent / "pages"


class Content:
    name: str
    content: str
    markdown: str
    summary: str
    hex: str
    soup: bs4.BeautifulSoup

    def __init__(self, url: str):
        self.url: str = url

    @alru_cache(maxsize=128)
    async def fetch(self, model: openai.Client = None, token: str = None):
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
                if (model is not None) and (token is not None):
                    await self.summarize_url(model, token)

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
    def from_json(cls, data: dict | pathlib.Path) -> "Content":
        if isinstance(data, pathlib.Path):
            data = json.loads(data.read_text())
        content = cls(data["url"])
        content.hex = data["hex"]
        content.content = data["content"]
        content.markdown = data["markdown"]
        content.name = data.get("name")
        content.summary = data.get("summary")
        return content

    async def summarize_url(self, model, token) -> dict:
        summary = "\n".join(
            await model_querying.query_text_model(
                token,
                (
                    "Your job is to summarize downloaded html web-pages that have been transformed to markdown. "
                    "You will be used in an automated agent-pattern without human supervision, summarize the following in at most 3 sentences."
                ),
                [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"---\nFETCHED URL NAME: {self.name}\nCONTENTS:\n{self.markdown}\n---\n",
                            }
                        ],
                    }
                ],
                model=model,
            )
        )
        self.summary = summary

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
        self.contents: dict[str, Content] = {}

    def add(self, content: Content):
        self.contents[content.url] = content
        self.save()

    def save(self):
        for _, content in self.contents.items():
            (self.cache_dir / f"{content.hex}.json").write_text(json.dumps(content))

    def load(self):
        for file in CACHE.glob("*.json"):
            content = Content.from_json(file)
            self.contents[content.url] = content

    async def fetch_content(self, url: str) -> Content:
        if url in self.contents:
            return self.contents[url]
        else:
            content = Content(url)
            await content.fetch()
            self.add(content)
            return content

    def to_dict(self) -> dict:
        return {url: content.to_dict() for url, content in self.contents.items()}

    def to_openai(self) -> list[dict]:
        return [content.format_for_openai() for _, content in self.contents.items()]
