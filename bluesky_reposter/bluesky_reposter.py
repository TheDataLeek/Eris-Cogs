import re
import os
import json

import typer
from rich import print
import discord
from redbot.core import commands, data_manager, Config, checks, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
import atproto

app = typer.Typer()

BaseCog = getattr(commands, "Cog", object)

RETYPE = type(re.compile("a"))


class BlueskyReposter(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot: bot.Red = bot_instance
        self.config = Config.get_conf(
            self,
            identifier=3248975002349,
            force_registration=True,
            cog_name="BlueskyReposter",
        )

        self.config.register_global(json_config="{}", seen=[])

        self.scheduler = AsyncIOScheduler(
            jobstores={"default": MemoryJobStore()},
        )
        self.scheduler.start()

        async def check_for_posts():
            config_contents = await self.config.json_config()
            config = json.loads(config_contents)
            server: discord.Guild = self.bot.get_guild(config["server"])
            hooks = config["hooks"]
            auth = await self.get_bluesky_auth()
            for handle, channel_id in hooks.items():
                channel: discord.TextChannel = server.get_channel(channel_id)
                posts: list[atproto.models.AppBskyFeedDefs.PostView] = (
                    fetch_recent_reposts(
                        handle.replace("@", "."),
                        user=auth["user"],
                        passwd=auth["pass"],
                    )
                )
                async with self.config.seen() as seen_posts:
                    post: atproto.models.AppBskyFeedDefs.PostView
                    for post in posts:
                        if post.uri in seen_posts:
                            continue
                        uri_parts = re.split(r"/+", post.uri)
                        did = uri_parts[1]
                        rkey = uri_parts[3]
                        url = f"https://bsky.app/profile/{did}/post/{rkey}"
                        await channel.send(url)
                        seen_posts.append(post.uri)

        self.scheduler.add_job(
            check_for_posts,
            trigger=IntervalTrigger(minutes=1),
            replace_existing=True,
            id="BlueskyReposter",
            name="BlueskyReposter",
        )

    @commands.command()
    @checks.mod()
    @checks.bot_in_a_guild()
    async def configure_bluesky(self, ctx):
        """
        Set config in the format -
        {
            "server": "id",
            "hooks": {
                "handle": "channel_id", ...
            }
        }
        """
        message: discord.Message = ctx.message
        contents = " ".join(message.clean_content.split(" ")[1:])  # skip command
        await self.config.json_config.set(contents)
        await ctx.send("Done")

    @commands.command()
    @checks.mod()
    @checks.bot_in_a_guild()
    async def show_bluesky(self, ctx):
        """
        Set accounts to follow
        """
        config_contents = await self.config.json_config()
        formatted = json.dumps(json.loads(config_contents), indent=4)
        await ctx.send(f"```\n{formatted}\n```")

    async def get_bluesky_auth(self):
        self.bluesky_settings = await self.bot.get_shared_api_tokens("bluesky")
        return self.bluesky_settings


@app.command()
def fetch_recent_reposts(
    account: str,
    user: str = None,
    passwd: str = None,
) -> list[atproto.models.AppBskyFeedDefs.PostView]:
    client = atproto.Client()
    client.login(user or os.environ["BSKY_USER"], passwd or os.environ["BSKY_PASS"])
    did = client.resolve_handle(account).did
    data: atproto.models.AppBskyFeedGetAuthorFeed.Response = client.get_author_feed(
        actor=did,
        limit=10,
    )
    posts = []
    post: atproto.models.AppBskyFeedDefs.FeedViewPost
    for post in data.feed:
        post_view: atproto.models.AppBskyFeedDefs.PostView = post.post
        posts.append(post_view)
    return posts


if __name__ == "__main__":
    app()
