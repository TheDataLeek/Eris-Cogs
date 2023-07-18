#!/usr/bin/env python3

import os
import discord
from redbot.core import utils, data_manager, commands, Config, checks
from redbot.core.utils import embed
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
import sqlite3 as sq

from pprint import pprint as pp

from typing import Optional, Union, Dict

import pathlib
import random

BaseCog = getattr(commands, "Cog", object)


class GoodBot(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.whois = self.bot.get_cog("WhoIs")

        data_dir: pathlib.Path = data_manager.bundled_data_path(self)
        self.names = [s for s in (data_dir / "names.txt").read_text(encoding='utf-8').split("\n") if s]
        self.good = [s for s in (data_dir / "good.txt").read_text(encoding='utf-8').split("\n") if s]
        self.bad = [s for s in (data_dir / "bad.txt").read_text(encoding='utf-8').split("\n") if s]

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

        self._update_cache()

    def _update_cache(self):
        self.emojis = {str(e.id): e for e in self.bot.emojis}

    @commands.command()
    @checks.mod()
    async def set_rating_threshold(self, ctx, which: str, thresh: int):
        """
        Sets the threshold for the goodbot compliment

        which: `good` or `bad` to determine which threshold you're setting
        thresh: the number of emoji it requires
        """
        if thresh < 1:
            await ctx.send("Please set a reasonable bound")
            return

        if which not in ['good', 'bad']:
            await ctx.send("Please provide `good` or `bad` as input!")
            return

        async with self.config.settings() as settings:
            if which == 'good':
                settings["good_thresh"] = thresh
            else:
                settings["bad_thresh"] = thresh

        await ctx.send(f"Success, new {which} threshold has been set to {thresh}")

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
            has_been_noticed = messagetracking.get(str(msg.id), False)
            good_thresh = int(settings["good_thresh"])
            bad_thresh = int(settings["bad_thresh"])
            if not has_been_noticed:
                if reaction.emoji == '👍' and reaction.count >= good_thresh:
                    phrase = self.generate_message(og_author, good=True)
                elif reaction.emoji == "👎" and reaction.count >= bad_thresh:
                    phrase = self.generate_message(og_author, good=False)
                elif reaction.count >= good_thresh:
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

    @commands.command(aliases=["ratings"])
    async def rating(
        self,
        ctx,
        user: Optional[discord.Member] = None,
        which: Optional[str] = "guild",
        full: Optional[bool] = False,
    ):
        """
        See the top 10 emoji scores for a user for either the current guild OR overall
        """
        if user is None:
            user = ctx.author

        self._update_cache()

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
            # if (len(eid) < 5) or (eid in self.emojis)
        }
        scores = [(emoji, count) for emoji, count in scores.items() if emoji]
        scores = sorted(scores, key=lambda tup: -tup[1])

        if not full:
            scores = scores[:10]

        formatted = []
        for emoji, count in scores:
            formatted.append(f"{str(emoji)} = {count}")

        formatted = "\n".join(formatted)

        embedded_response = discord.Embed(
            title=f"Scores for {user.display_name}",
            type="rich",
            description=formatted,
        )
        embedded_response = embed.randomize_colour(embedded_response)
        await ctx.send(embed=embedded_response)

    @commands.command()
    async def allratings(self, ctx, which: Optional[str] = "guild"):
        """
        See the top 10 emoji scores for a user for either the current guild OR overall
        """
        self._update_cache()

        scores: Dict
        if which == "guild":
            async with self.config.guild(ctx.guild).scores() as guildscores:
                scores = guildscores
        else:
            async with self.config.scores() as globalscores:
                scores = globalscores

        # iterate through users in [total num of emoji] descending if they are in the server
        users = []
        score_list = [
            (ctx.guild.get_member(int(userid)), obj, sum(list(obj.values())))
            for userid, obj in scores.items()
            if ctx.guild.get_member(int(userid)) is not None
        ]
        for user, obj, total in sorted(score_list, key=lambda tup: -tup[2]):
            # convert eid:count obj to emoji:count
            emoji = {
                self.emojis.get(str(eid), eid): cnt
                for eid, cnt in obj.items()
                # if (len(eid) < 5) or (eid in self.emojis)
            }
            # prune missing
            emoji = [(e, c) for e, c in emoji.items() if e]
            # sort
            emoji = sorted(emoji, key=lambda tup: -tup[1])
            # limit to top 3
            emoji = emoji[:3]
            # format
            emoji = ", ".join(f"{e} ({c})" for e, c in emoji)
            users.append(f"{user.display_name} [{total}] - {emoji}")

        response = "\n".join(users)

        pages = list(pagify(response))
        await menu(ctx, pages, DEFAULT_CONTROLS)

        embedded_response = discord.Embed(
            title=f"All Scores for {ctx.guild.name if which == 'guild' else 'Everyone'}",
            type="rich",
            description=response,
        )
        # embedded_response = embed.randomize_colour(embedded_response)
        # await ctx.send(embed=embedded_response)
