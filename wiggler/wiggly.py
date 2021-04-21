# stdlib
import random
import re

from typing import Optional, List

# third party
import discord
from redbot.core import commands, bot, checks, Config

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)


class Wiggle(BaseCog, ErisEventMixin):
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
            if not len(emojis) and ctx.author.id in wigglelist:
                del wigglelist[ctx.author.id]
                await ctx.send('Success, reactions removed for user.')
            else:
                wigglelist[ctx.author.id] = [e.id for e in emojis]
                await ctx.send('Success, emoji set.')

    @wiggle.command()
    @checks.mod()
    async def show(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        async with self.config.guild(ctx.guild).wiggle() as wigglelist:
            for userid, emojiids in wigglelist.items():
                user: discord.Member = guild.get_member(userid)
                emoji: emoji.Emoji = random.choice([self.emojis[e] for e in emojiids])
                await ctx.send(f"{str(emoji)} for {user.nick}")


    async def wiggle_handler(self, message: discord.message):
        ctx = await self.bot.get_context(message)

        async with self.lock_config.channel(message.channel).get_lock(), self.config.guild(ctx.guild).wiggle() as wigglelist:
            author = ctx.message.author
            allowed: bool = await self.allowed(ctx, message)
            allowed &= random.random() <= 0.05
            allowed &= author.id in wigglelist

            emoji = random.choice([self.emojis[e] for e in wigglelist[author.id]])
            await message.add_reaction(emoji)
