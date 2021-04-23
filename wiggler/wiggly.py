# stdlib
import random
import re

from typing import Optional, List

# third party
import discord
from redbot.core import commands, bot, checks, Config
from redbot.core.utils import embed
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

BaseCog = getattr(commands, "Cog", object)


class Wiggle(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.emojis = {str(e.id): e for e in self.bot.emojis}

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
        """Group for wiggle commands"""
        pass

    @wiggle.command()
    async def set(self, ctx: commands.Context, *emojis: discord.Emoji):
        """
        Set a list of emoji for snek to alternate through
        """
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            authorid = str(ctx.author.id)
            if not len(emojis) and authorid in wigglelist:
                del wigglelist[authorid]
                await ctx.send("Success, reactions removed for user.")
            else:
                wigglelist[authorid] = [str(e.id) for e in emojis]
                await ctx.send("Success, emoji set.")

    @wiggle.command()
    @checks.mod()
    async def setfor(
        self, ctx: commands.Context, user: discord.Member, *emojis: discord.Emoji
    ):
        """
        Set a list of emoji for snek to alternate through for another user
        """
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            userid = str(user.id)
            if not len(emojis) and userid in wigglelist:
                del wigglelist[userid]
                await ctx.send("Success, reactions removed for user.")
            else:
                wigglelist[userid] = [str(e.id) for e in emojis]
                await ctx.send("Success, emoji set.")

    @wiggle.command()
    async def show(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """
        Show your set emoji reacts
        """
        self.emojis = {str(e.id): e for e in self.bot.emojis}

        if user is None:
            author: discord.Member = ctx.author
        else:
            author: discord.Member = user
        authorid: str = str(author.id)
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            if authorid in wigglelist:
                emojis: List[discord.Emoji] = [
                    self.emojis[e] for e in wigglelist[authorid]
                ]

                formatted = f"{' '.join([str(e) for e in emojis])}"

                embedded_response = discord.Embed(
                    title=f"Wiggle Emoji for {author.display_name}",
                    type="rich",
                    description=formatted,
                )
                embedded_response = embed.randomize_colour(embedded_response)
                await ctx.send(embed=embedded_response)

    @wiggle.command()
    @checks.mod()
    async def showall(self, ctx: commands.Context):
        """
        Show all emoji reacts for all users in guild
        """
        self.emojis = {str(e.id): e for e in self.bot.emojis}

        guild: discord.Guild = ctx.guild
        formatted = []
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            for userid, emojiids in wigglelist.items():
                user: discord.Member = guild.get_member(int(userid))
                emojis: List[discord.Emoji] = [self.emojis[str(e)] for e in emojiids]
                line = f"{' '.join([str(e) for e in emojis])} for {user.display_name}"
                formatted.append(line)
                # await ctx.send(line)

        formatted = '\n'.join(formatted)
        pages = list(pagify(formatted, page_length=1000))
        await menu(ctx, pages, DEFAULT_CONTROLS)
        # embedded_response = discord.Embed(
        #     title=f"Wiggle Emoji for {ctx.guild.name}",
        #     type="rich",
        #     description=formatted,
        # )
        # embedded_response = embed.randomize_colour(embedded_response)
        # await ctx.send(embed=embedded_response)


    async def wiggle_handler(self, message: discord.message):
        # don't proc on DMs
        if message.guild is None:
            return

        self.emojis = {str(e.id): e for e in self.bot.emojis}

        ctx = await self.bot.get_context(message)
        authorid = str(ctx.author.id)

        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            allowed: bool = random.random() <= 0.05
            allowed &= authorid in wigglelist
            if not allowed:
                return

            if random.random() <= 0.1:
                for emojiid in wigglelist[authorid]:
                    emoji = self.emojis[emojiid]
                    await message.add_reaction(emoji)
            else:
                emojids = wigglelist[authorid]
                emojis = [self.emojis[e] for e in emojids]
                emoji = random.choice(emojis)
                await message.add_reaction(emoji)
