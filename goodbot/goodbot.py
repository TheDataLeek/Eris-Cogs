#!/usr/bin/env python3

import os
import discord
from redbot.core import utils, data_manager, commands, Config, checks
import sqlite3 as sq

import pprint as pp

from typing import Optional, Union

import pathlib
import random

BaseCog = getattr(commands, "Cog", object)


class GoodBot(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.whois = self.bot.get_cog("WhoIs")

        self.emojis = {str(e.id): e for e in self.bot.emojis}

        data_dir: pathlib.Path = data_manager.bundled_data_path(self)
        self.names = [s for s in (data_dir / "names.txt").read_text().split("\n") if s]
        self.good = [s for s in (data_dir / "good.txt").read_text().split("\n") if s]
        self.bad = [s for s in (data_dir / "bad.txt").read_text().split("\n") if s]

        self.config = Config.get_conf(
            self,
            identifier=7846324170810587603284975287,
            force_registration=True,
            cog_name="goodbot",
        )

        default_global = {"scores": {}, "settings": {"thresh": 7}}
        default_guild = {
            "scores": {},
            "messages": {},
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        bot.add_listener(self.parse_reaction_add, "on_reaction_add")
        bot.add_listener(self.parse_reaction_remove, "on_reaction_remove")

        self.legacyfile = os.path.join(
            str(pathlib.Path.home()), "bots.db"
        )  # for old version

    @commands.command()
    @checks.mod
    async def set_rating_threshold(
            self, ctx, thresh: int
    ):
        """
        Sets the threshold for the goodbot compliment
        """
        if thresh < 1:
            await ctx.send("Please set a reasonable bound")
            return

        async with self.config.settings() as settings:
            settings["thresh"] = thresh

        await ctx.send(f"Success, new threshold has been set to {thresh}")


    def generate_message(self, author: discord.Member, good=True) -> str:
        phrase = "{} IS A {} {}".format(
            author.mention,
            random.choice(self.good if good else self.bad).upper(),
            random.choice(self.names).upper(),
        )
        return phrase

    async def track_user(
        self,
        ctx: commands.Context,
        author: discord.Member,
        reaction: discord.Reaction,
        initial_val=1,
        step=1,
    ):
        # track user scores
        async with self.config.guild(
            ctx.guild
        ).scores() as guildscores, self.config.scores() as globalscores:
            # convert emoji to str (leave if unicode)
            reaction_emoji: Union[discord.Emoji, str] = reaction.emoji
            reactionid = reaction_emoji
            if not isinstance(reaction_emoji, str):
                reactionid = str(reaction_emoji.id)

            # initialize and collect in counters
            for D in [guildscores, globalscores]:
                if str(author.id) not in D:
                    D[str(author.id)] = {}

                if reactionid not in D[str(author.id)]:
                    D[str(author.id)][reactionid] = initial_val
                else:
                    D[str(author.id)][reactionid] += step
                    if D[str(author.id)][reactionid] == 0:
                        del D[str(author.id)][reactionid]

    async def parse_reaction_add(
        self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]
    ):
        """
        User is the user that added the reaction
        """
        # Prevent acting on DM's and if the bot reacted
        if reaction.message.guild is None or user.bot:
            return

        ctx: commands.Context = await self.bot.get_context(reaction.message)
        msg: discord.Message = reaction.message
        og_author: discord.Member = msg.author

        # check if we've hit the threshold and notify if so
        async with self.config.settings() as settings, self.config.guild(
            ctx.guild
        ).messages() as messagetracking:
            thresh = int(settings["thresh"])
            has_been_noticed = messagetracking.get(str(msg.id), False)
            if not has_been_noticed and reaction.count >= thresh:
                if reaction.emoji == "👍":
                    phrase = self.generate_message(og_author, good=True)
                elif reaction.emoji == "👎":
                    phrase = self.generate_message(og_author, good=False)
                else:
                    phrase = f"{og_author.mention} has been {reaction.emoji}'d"
                await ctx.send(phrase, reference=reaction.message)

                messagetracking[str(msg.id)] = True

        await self.track_user(ctx, og_author, reaction)

    async def parse_reaction_remove(self, reaction, user):
        """
        User is the user that added the reaction
        """
        # Prevent acting on DM's and if the bot reacted
        if reaction.message.guild is None or user.bot:
            return

        ctx: commands.Context = await self.bot.get_context(reaction.message)
        msg: discord.Message = reaction.message
        og_author: discord.Member = msg.author

        await self.track_user(ctx, og_author, reaction, initial_val=1, step=-1)

    async def getuser(self, ctx: commands.Context, authorid: str) -> Optional[str]:
        if self.whois is not None:
            realname = self.whois.convert_realname(
                await self.whois.get_realname(ctx, authorid)
            )
            return realname

    @commands.command()
    async def rating(
        self, ctx, user: Optional[discord.Member] = None, which: Optional[str] = "guild"
    ):
        """
        See the top 10 emoji scores for a user for either the current guild OR overall
        """
        if user is None:
            user = ctx.author

        async with self.config.guild(
            ctx.guild
        ).scores() as guildscores, self.config.scores() as globalscores:
            user_guild_scores = guildscores.get(str(user.id), {})
            user_global_scores = globalscores.get(str(user.id), {})

        if which == "guild":
            scores = user_guild_scores
        else:
            scores = user_global_scores

        scores = {
            self.emojis.get(str(eid), eid): cnt
            for eid, cnt in scores.items()
            if (len(eid) < 5) or (eid in self.emojis)
        }
        scores = [(emoji, count) for emoji, count in scores.items() if emoji]

        formatted = [f"Scores for {user.mention}"]
        for emoji, count in sorted(scores, key=lambda tup: -tup[1]):
            formatted.append(f"{str(emoji)} = {count}")

        formatted = "\n".join(formatted)
        await ctx.send(formatted)
