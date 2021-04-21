# stdlib
import random
import re

from typing import Optional, List

# third party
import discord
from redbot.core import commands, bot, checks, Config

BaseCog = getattr(commands, "Cog", object)


class Wiggle(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.emojis = {e.id: e for e in self.bot.emojis}

        self.config = Config.get_conf(
            self,
            identifier=8766782347657182931290319283,
            force_registration=True,
            cog_name="wiggle",
        )

        default_guild = {
            "wiggle": {},
        }
        self.config.register_guild(**default_guild)

        self.bot.add_listener(self.wiggle_handler, "on_message")

    @commands.group()
    async def wiggle(self, ctx: commands.Context):
        pass

    @wiggle.command()
    async def set(self, ctx: commands.Context, *emojis: discord.Emoji):
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            authorid = str(ctx.author.id)
            if not len(emojis) and authorid in wigglelist:
                del wigglelist[authorid]
                await ctx.send("Success, reactions removed for user.")
            else:
                wigglelist[authorid] = [e.id for e in emojis]
                await ctx.send("Success, emoji set.")

    @wiggle.command()
    async def show(self, ctx: commands.Context):
        author: discord.Member = ctx.author
        authorid: str = str(author.id)
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            if authorid in wigglelist:
                emojis: List[discord.Emoji] = [self.emojis[e] for e in wigglelist[authorid]]
                await ctx.send(
                    f"{' '.join([str(e) for e in emojis])} for {author.display_name}"
                )

    @wiggle.command()
    @checks.mod()
    async def showall(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            for userid, emojiids in wigglelist.items():
                user: discord.Member = guild.get_member(int(userid))
                emojis: List[discord.Emoji] = [self.emojis[e] for e in emojiids]
                await ctx.send(
                    f"{' '.join([str(e) for e in emojis])} for {user.display_name}"
                )

    async def wiggle_handler(self, message: discord.message):
        ctx = await self.bot.get_context(message)
        authorid = str(ctx.author.id)

        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            allowed: bool = random.random() <= 0.05
            allowed &= authorid in wigglelist
            if not allowed:
                return

            emoji = random.choice([self.emojis[e] for e in wigglelist[authorid]])
            await message.add_reaction(emoji)
