#!/usr/bin/env python3

import os
import discord
from redbot.core import utils, data_manager, commands, Config
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
            "imported": False,
            "scores": {},
            "threshold": 7,
        }
        default_guild = {
            "scores": {}
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        bot.add_listener(self.parse_reaction_add, "on_reaction_add")
        bot.add_listener(self.parse_reaction_remove, "on_reaction_remove")

        self.legacyfile = os.path.join(str(pathlib.Path.home()), "bots.db")   # for old version

    async def parse_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        """
        User is the user that added the reaction
        """
        # Prevent acting on DM's and if the bot reacted
        if reaction.message.guild is None or user.bot:
            return

        ctx: commands.Context = await self.bot.get_context(reaction.message)

        async with self.config.guild(ctx.guild).scores() as guildscores, self.config.scores() as globalscores:
            pass

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
                await ctx.send(phrase, reference=reaction.message)
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
                await ctx.send(phrase, reference=reaction.message)
                # await bot.send_filtered(reaction.message.channel, content=phrase, reference=reaction.message)
                gb_instance.noticed.add(reaction.message.id)

        if rating is not None:
            await rate_user(reaction.message.author.id, rating)

    async def parse_reaction_remove(self, reaction, user):
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

