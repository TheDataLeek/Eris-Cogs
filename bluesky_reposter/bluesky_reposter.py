import sys
import json
import asyncio
import re
import os
import json
from typing import TypeVar, Any
from pathlib import Path
import pickle
import datetime
import math

import cyclopts
from rich import print
import discord
from redbot.core import commands, data_manager, Config, checks, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import BaseJobStore
from apscheduler.job import Job
import apscheduler.util as apscheduler_util
from apscheduler.jobstores.base import JobLookupError, ConflictingIdError
import atproto

app = cyclopts.App()

BaseCog = getattr(commands, "Cog", object)

RETYPE = type(re.compile("a"))
BskyEmbedType = TypeVar(
    "BskyEmbedType",
    atproto.models.AppBskyEmbedImages.View,
    atproto.models.AppBskyEmbedVideo.View,
    atproto.models.AppBskyEmbedExternal.View,
    atproto.models.AppBskyEmbedRecord.View,
    atproto.models.AppBskyEmbedRecordWithMedia.View,
)


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
        self.config.register_global(json_config="{}", seen=[], bad_config=False)

        self.data_dir = data_manager.bundled_data_path(self)
        self.jobstore = FileJobStore(memory_file=self.data_dir / 'jobstore.pkl')
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": self.jobstore},
        )

        job_id = "BlueskyReposter"
        self.scheduler.add_job(
            self.check_for_posts,
            trigger=IntervalTrigger(minutes=2),
            replace_existing=True,
            id=job_id,
            name=job_id,
        )

        self.scheduler.start()

    async def check_for_posts(self):
        if await self.config.bad_config():
            return

        config_contents = await self.config.json_config()
        try:
            config = json.loads(config_contents)
        except:  # noqa
            await self.config.bad_config.set(True)
            return

        server: discord.Guild = self.bot.get_guild(int(config["server"]))
        hooks = config["hooks"]
        auth = await self.get_bluesky_auth()
        for handle, channel_id in hooks.items():
            print(f"Placing posts from {handle} to {channel_id}")
            channel: discord.TextChannel = server.get_channel(int(channel_id))
            posts: list[atproto.models.AppBskyFeedDefs.PostView] = fetch_recent_reposts(
                handle.replace("@", "."),
                user=auth["user"],
                passwd=auth["pass"],
            )
            post: atproto.models.AppBskyFeedDefs.PostView
            author: atproto.models.AppBskyActorDefs.ProfileViewBasic
            seen_posts = await self.config.seen()
            for post in posts:
                if contents := await build_embed(handle, post, seen_posts):
                    await channel.send(embed=contents)
                    seen_posts.append(post.uri)
                    seen_posts = seen_posts[-1000:]
                    await self.config.seen.set(seen_posts)

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
        await self.config.bad_config.set(False)
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


async def build_embed(
    handle: str,
    post: atproto.models.AppBskyFeedDefs.PostView,
    seen_posts: list[str],
) -> None | discord.Embed:
    author: atproto.models.AppBskyActorDefs.ProfileViewBasic = post.author
    embed: BskyEmbedType = post.embed
    match embed:
        case atproto.models.AppBskyEmbedImages.View():
            if len(embed.images):
                image_url = embed.images[0].fullsize
        case atproto.models.AppBskyEmbedVideo.View():
            image_url = embed.playlist
        case atproto.models.AppBskyEmbedExternal.View():
            image_url = embed.external.uri
        case _:
            image_url = None

    uri_parts = re.split(r"/+", post.uri)
    did = uri_parts[1]
    rkey = uri_parts[3]
    url = f"https://bsky.app/profile/{did}/post/{rkey}"
    if post.uri in seen_posts:
        return None

    post_text_contents = post.record.text
    if post_text_contents:
        post_text_contents = f"{post_text_contents}\n"

    embed_description_contents = (
        f"Post by {author.display_name} ({author.handle})\n"
        f"{post_text_contents}"
        f"💬 {post.reply_count} ❤️ {post.like_count} 🔁 {post.repost_count}"
    )

    embed_response = (
        discord.Embed(
            title=f"{handle}🔁{author.handle}",
            type="rich",
            url=url,
            description=embed_description_contents,
        )
        .set_thumbnail(url=author.avatar)
        .set_image(url=image_url)
    )

    return embed_response


class FileJobStore(BaseJobStore):
    def __init__(self, memory_file: Path):
        self.memory_file = memory_file
        self.memory_file.parent.mkdir(exist_ok=True, parents=True)
        self.memory_file.touch()
        self.pickle_protocol = pickle.HIGHEST_PROTOCOL
        self.data = {}

    def _save_current_state_to_disk(self):
        memory = pickle.dumps(self.data, protocol=self.pickle_protocol)
        self.memory_file.write_bytes(memory)

    def _load_memory(self):
        self.data = pickle.loads(self.memory_file.read_bytes())

    def lookup_job(self, job_id):
        """
        Returns a specific job, or ``None`` if it isn't found..

        The job store is responsible for setting the ``scheduler`` and ``jobstore`` attributes of
        the returned job to point to the scheduler and itself, respectively.

        :param str|unicode job_id: identifier of the job
        :rtype: Job
        """
        if job_id in self.data:
            return self._job_from_storable(self.data[job_id])
        else:
            return None

    def get_due_jobs(self, now: datetime.datetime):
        """
        Returns the list of jobs that have ``next_run_time`` earlier or equal to ``now``.
        The returned jobs must be sorted by next run time (ascending).

        :param datetime.datetime now: the current (timezone aware) datetime
        :rtype: list[Job]
        """
        return [job for job in self.get_all_jobs() if job.next_run_time <= now]

    def get_next_run_time(self):
        """
        Returns the earliest run time of all the jobs stored in this job store, or ``None`` if
        there are no active jobs.

        :rtype: datetime.datetime
        """
        jobs = self.get_all_jobs()
        if jobs:
            return jobs[0].next_run_time
        else:
            return None

    def get_all_jobs(self):
        """
        Returns a list of all jobs in this job store.
        The returned jobs should be sorted by next run time (ascending).
        Paused jobs (next_run_time == None) should be sorted last.

        The job store is responsible for setting the ``scheduler`` and ``jobstore`` attributes of
        the returned jobs to point to the scheduler and itself, respectively.

        :rtype: list[Job]
        """
        joblist: list[Job] = []
        job: Job
        for job_id, storable in self.data.items():
            job = self._job_from_storable(storable)
            joblist.append(job)
        joblist = sorted(joblist, key=lambda job: apscheduler_util.datetime_to_utc_timestamp(job.next_run_time) if
        job.next_run_time else
        math.inf)
        return joblist


    def add_job(self, job: Job):
        """
        Adds the given job to this store.

        :param Job job: the job to add
        :raises ConflictingIdError: if there is another job in this store with the same ID
        """
        job_id = job.id
        if job_id in self.data:
            raise ConflictingIdError(job_id)
        else:
            self.data[job_id] = self._job_to_storable(job)
            self._save_current_state_to_disk()

    def update_job(self, job: Job):
        """
        Replaces the job in the store with the given newer version.

        :param Job job: the job to update
        :raises JobLookupError: if the job does not exist
        """
        job_id = job.id
        if job_id in self.data:
            self.data[job_id] = self._job_to_storable(job)
            self._save_current_state_to_disk()
        else:
            raise JobLookupError(job_id)

    def remove_job(self, job_id):
        """
        Removes the given job from this store.

        :param str|unicode job_id: identifier of the job
        :raises JobLookupError: if the job does not exist
        """
        if job_id in self.data:
            del self.data[job_id]
            self._save_current_state_to_disk()
        else:
            raise JobLookupError(job_id)

    def remove_all_jobs(self):
        """Removes all jobs from this store."""
        self.data = {}
        self._save_current_state_to_disk()

    def _job_to_storable(self, job: Job):
        # we pickle here to ensure it's not mutable by accident
        return {
            "_id": job.id,
            "next_run_time": apscheduler_util.datetime_to_utc_timestamp(job.next_run_time),
            "job_state": pickle.dumps(job.__getstate__(), protocol=self.pickle_protocol)
        }

    def _job_from_storable(self, storable: dict[str, Any]):
        job_state = pickle.loads(storable["job_state"])
        job = Job.__new__(Job)
        job.__setstate__(job_state)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        return job


@app.command()
def fetch_recent_reposts(
    account: str,
    user: str = None,
    passwd: str = None,
) -> list[atproto.models.AppBskyFeedDefs.PostView]:
    client = atproto.Client()
    try:
        user = os.environ.get('BSKY_USER', user)
        print(f"Authenticating to Bluesky as {user}")
        passwd = os.environ.get('BSKY_PASS', passwd)
        client.login(user, passwd)
    except Exception as e:
        print(f"Error occurred while logging in!\n{e}")
        sys.exit(1)
    did = client.resolve_handle(account).did
    data: atproto.models.AppBskyFeedGetAuthorFeed.Response = client.get_author_feed(
        actor=did,
        limit=15,
    )
    posts = []
    post: atproto.models.AppBskyFeedDefs.FeedViewPost
    for post in data.feed:
        post_view: atproto.models.AppBskyFeedDefs.PostView = post.post
        posts.append(post_view)
    posts = posts[::-1]  # flip to chronological
    return posts


@app.default
def test(account: str, user: str | None = None, passwd: str | None = None):
    posts = fetch_recent_reposts(account, user, passwd)
    for post in posts:
        embed: discord.Embed = asyncio.run(build_embed(account, post, []))
        print(embed.to_dict())


if __name__ == "__main__":
    app()
