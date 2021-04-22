#!/usr/bin/env python3

import os
import discord
from redbot.core import utils, data_manager, commands, Config
import sqlite3 as sq

import pprint as pp

from typing import Optional

import pathlib
import random

BaseCog = getattr(commands, "Cog", object)


RATINGSFILE = os.path.join(str(pathlib.Path.home()), "bots.db")



def user_exists(userid, cursor=None):
    if cursor is None:
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
    else:
        c = cursor

    c.execute("SELECT * FROM ratings WHERE userid=?", (userid,))

    results = c.fetchall()

    exists = False

    if len(results) != 0:
        exists = True

    if cursor is None:
        con.close()

    return exists


def get_user_rating(userid, cursor=None):
    if cursor is None:
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
    else:
        c = cursor

    c.execute("SELECT good, bad FROM ratings WHERE userid=?", (userid,))

    results = c.fetchall()

    rating = None

    if len(results) != 0:
        rating = (results[0][0], results[0][1])
    else:
        # Add if doesn't exist, hopefully prevent crashes
        c.execute(
            "INSERT INTO ratings(userid, good, bad) VALUES(?,?,?)", (userid, 0, 0)
        )
        con.commit()

    if cursor is None:
        con.close()

    return rating


class GoodBot(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.whois = self.bot.get_cog("WhoIs")

        data_dir: pathlib.Path = data_manager.bundled_data_path(self)
        self.names = [s for s in (data_dir / 'names.txt').read_text().split('\n') if s]
        self.good = [s for s in (data_dir / 'good.txt').read_text().split('\n') if s]
        self.bad = [s for s in (data_dir / 'bad.txt').read_text().split('\n') if s]

        self.config = Config.get_conf(
            self,
            identifier=7846324170810587603284975287,
            force_registration=True,
            cog_name="goodbot",
        )

        default_global = {
            "scores": {}
        }
        default_guild = {
            "scores": {}
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        self.previous_author = dict()
        self.noticed = set()

    async def getuser(self, ctx: commands.Context, authorid: str) -> Optional[str]:
        if self.whois is not None:
            realname = self.whois.convert_realname(
                await self.whois.get_realname(ctx, authorid)
            )
            return realname

    @commands.command()
    async def rating(self, ctx, user: discord.Member = None):
        """
        Displays a user rating in the form <score> (<updoots>/<downdoots>/<totaldoots>)
        """
        if user is None:
            user = ctx.author

        if not user_exists(user.id):
            await ctx.send("{} hasn't been rated".format(user.mention))
            return

        good, bad = get_user_rating(user.id)

        await ctx.send("User {} has a score of {}".format(user.mention, good - bad))

    @commands.command()
    async def goodbots(self, ctx):
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
        c.execute("SELECT userid, good, bad from ratings ORDER BY (good - bad) DESC")
        db_results = c.fetchall()
        results = []
        for userid, good, bad in db_results:
            try:
                user = ctx.guild.get_member(int(userid))
                if user is not None:
                    results.append(
                        (
                            user.nick,
                            good,
                            bad,
                            good - bad,
                            100 * (good - bad) / (good + bad),
                        )
                    )
            except Exception as e:
                print(e)
                pass
        results.sort(key=lambda tup: -tup[-2])
        results = [
            "{}  -> {} - {} = {} ({:0.02f}% positive)".format(*row) for row in results
        ]
        await ctx.send("Scores:")
        for i in range(0, len(results), 20):
            await ctx.send("```{}```".format("\n".join(results[i : i + 20])))
        con.close()

    @commands.command()
    async def see_previous(self, ctx):
        if ctx.message.author.id != "142431859148718080":
            return
        resolved_previous = {
            self.bot.get_guild(server_id).name: {
                self.bot.get_channel(channel_id)
                .name: self.bot.get_guild(server_id)
                .get_member(user_id)
                .name
                for channel_id, user_id in channels.items()
            }
            for server_id, channels in self.previous_author.items()
        }
        pretty_version = pp.pformat(resolved_previous)
        await ctx.send("```{}```".format(pretty_version))


def generate_handlers(bot, gb_instance):
    async def goodbot(message, reaction=None, action=None):
        # Prevent snek from voting on herself or counting
        # if bot.user.id == message.author.id:
        #     return

        # Prevent acting on DM's
        if message.guild is None:
            return

        clean_message = message.clean_content.lower()
        server = message.guild.id
        channel = message.channel.id

        rating = None
        if "good bot" in clean_message:
            rating = (1, 0)
        elif "bad bot" in clean_message:
            rating = (0, 1)
        else:
            prev_author = message.author.id
            if server not in gb_instance.previous_author:
                gb_instance.previous_author[server] = dict()
            gb_instance.previous_author[server][channel] = prev_author

        if (
            (rating is not None)
            and (gb_instance.previous_author[server].get(channel) is not None)
            and (gb_instance.previous_author[server][channel] != message.author.id)
        ):
            await rate_user(gb_instance.previous_author[server][channel], rating)

    async def rate_user(userid, rating):
        con = sq.connect(RATINGSFILE)
        c = con.cursor()
        if not user_exists(userid):
            c.execute(
                "INSERT INTO ratings(userid, good, bad) VALUES(?,?,?)",
                (userid, *rating),
            )
            con.commit()
        else:
            oldgood, oldbad = get_user_rating(userid, cursor=c)
            good, bad = (oldgood + rating[0], oldbad + rating[1])
            # MM: You've had your fun
            # if ((userid == '142431859148718080') and ((good - bad) <= 0)):
            #     bad = good - 3
            c.execute(
                "UPDATE ratings SET good=?, bad=? WHERE userid=?", (good, bad, userid)
            )
            con.commit()
        con.close()

    async def parse_reaction_add(reaction, user):
        # Prevent acting on DM's
        if reaction.message.guild is None:
            return

        server = reaction.message.guild.id
        channel = reaction.message.channel.id

        context = await bot.get_context(reaction.message)

        LIMIT = 7

        rating = None  # (+, -)
        # MM: you've had your fun
        # Upvote SpatulaFish
        # if reaction.emoji in ['👎', '👍'] and reaction.message.author.id == '142431859148718080':
        #     rating = (1, 0)
        if reaction.emoji == "👎":
            # MM proposal:
            # Element of randomness: Self downvotes could result in updoot
            if user.id == reaction.message.author.id:
                if random.random() < 0.5:
                    rating = (1, 0)
                else:
                    rating = (0, 1)
            else:
                rating = (0, 1)
            # MM proposal:
            # Just call the poor sod a bad bot
            # if ((reaction.message.author.id != '142431859148718080') and (reaction.count >= 5)):
            #     await bot.delete_message(reaction.message)
            if (reaction.count >= LIMIT) and (
                reaction.message.id not in gb_instance.noticed
            ):
                phrase = "{} IS A {} {}".format(
                    reaction.message.author.mention,
                    random.choice(badwords).upper(),
                    random.choice(names).upper(),
                )
                await context.send(phrase, reference=reaction.message)
                # await bot.send_filtered(reaction.message.channel, content=phrase, reference=reaction.message)
                gb_instance.noticed.add(reaction.message.id)
        elif reaction.emoji == "👍":
            # Downvote for self votes
            if user.id == reaction.message.author.id:
                rating = (0, 1)
            else:
                rating = (1, 0)
            if (reaction.count >= LIMIT) and (
                reaction.message.id not in gb_instance.noticed
            ):
                phrase = "{} IS A {} {}".format(
                    reaction.message.author.mention,
                    random.choice(goodwords).upper(),
                    random.choice(names).upper(),
                )
                await context.send(phrase, reference=reaction.message)
                # await bot.send_filtered(reaction.message.channel, content=phrase, reference=reaction.message)
                gb_instance.noticed.add(reaction.message.id)

        if rating is not None:
            await rate_user(reaction.message.author.id, rating)

    async def parse_reaction_remove(reaction, user):
        # Prevent acting on DM's
        if reaction.message.guild is None:
            return

        server = reaction.message.guild.id
        channel = reaction.message.channel.id

        rating = None
        # do nothing for remove, already punished once for self votes
        if user.id == reaction.message.author.id:
            return
        elif reaction.emoji == "👎":
            rating = (1, 0)
        elif reaction.emoji == "👍":
            rating = (0, 1)
        else:
            return

        await rate_user(reaction.message.author.id, rating)

    return goodbot, parse_reaction_add, parse_reaction_remove
