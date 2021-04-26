# stdlib
import random
import re
from pprint import pprint as pp

from typing import Optional, List, Union

# third party
import discord
from redbot.core import commands, bot, checks, Config
from redbot.core.utils import embed
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

BaseCog = getattr(commands, "Cog", object)


class AutoReact(BaseCog):
    def __init__(self, bot_instance: bot):
        super().__init__()

        self.bot = bot_instance

        self.emojis = {str(e.id): e for e in self.bot.emojis}

        self.config = Config.get_conf(
            self,
            identifier=982035871304957,
            force_registration=True,
            cog_name="autoreact",
        )

        default_guild = {
            "autoreact": {},
            "automsg": {},
            "channel": {},
        }
        self.config.register_guild(**default_guild)

        self.bot.add_listener(self.autoreact_handler, "on_message")
        self.bot.add_listener(self.channel_handler, "on_message")

    def convert_from_ids(self, emoji_ids: List[str]) -> List[Union[str, discord.Emoji]]:
        self.emojis = {str(e.id): e for e in self.bot.emojis}
        converted = []
        for eid in emoji_ids:
            try:
                int(eid)
                emoji = self.emojis.get(str(eid), None)
                if emoji:
                    converted.append(emoji)
            except ValueError:
                converted.append(eid)
        return converted

    @commands.group()
    async def autoreact(self, ctx: commands.Context):
        """Group for autoreact commands"""
        pass

    @autoreact.command()
    @checks.mod()
    async def channel(
        self, ctx, channel: discord.TextChannel, *emojis: Union[str, discord.Emoji]
    ):
        """
        Set a list of emoji to react with in the channel
        """
        channelid = str(channel.id)
        async with self.config.guild(ctx.guild).channel() as channeldict:
            if not len(emojis) and channelid in channeldict:
                del channeldict[channelid]
                await ctx.send("Success, reactions removed for user.")
            else:
                converted = []
                for e in emojis:
                    if isinstance(e, discord.Emoji):
                        converted.append(str(e.id))
                    else:
                        converted.append(e)
                channeldict[channelid] = converted
                await ctx.send("Success, emoji set.")

    @autoreact.command()
    @checks.mod()
    async def set(
        self,
        ctx: commands.Context,
        user: discord.Member,
        *emojis: Union[str, discord.Emoji],
    ):
        """
        Set a list of emoji to react with
        """
        async with self.config.guild(ctx.guild).autoreact() as autoreactdict:
            userid = str(user.id)
            if not len(emojis) and userid in autoreactdict:
                del autoreactdict[userid]
                await ctx.send("Success, reactions removed for user.")
            else:
                converted = []
                for e in emojis:
                    if isinstance(e, discord.Emoji):
                        converted.append(str(e.id))
                    else:
                        converted.append(e)
                autoreactdict[userid] = converted
                await ctx.send("Success, emoji set.")

    @autoreact.command()
    @checks.mod()
    async def msg(self, ctx: commands.Context, user: discord.Member, *msg: str):
        """
        Set a list of emoji to react with
        """
        async with self.config.guild(ctx.guild).automsg() as automsgdict:
            userid = str(user.id)
            if len(msg) == 0 and userid in automsgdict:
                del automsgdict[userid]
                await ctx.send("Success, messages removed for user.")
            else:
                msg = " ".join(msg)
                automsgdict[userid] = msg
                await ctx.send("Success, message set.")

    @autoreact.command()
    @checks.mod()
    async def show(self, ctx: commands.Context):
        """
        Show all emoji reacts for all users in guild
        """
        self.emojis = {str(e.id): e for e in self.bot.emojis}

        guild: discord.Guild = ctx.guild
        formatted = []
        async with self.config.guild(
            ctx.guild
        ).autoreact() as autoreactdict, self.config.guild(
            ctx.guild
        ).automsg() as automsgdict, self.config.guild(
            ctx.guild
        ).channel() as channeldict:
            for userid, emojiids in autoreactdict.items():
                user: discord.Member = guild.get_member(int(userid))
                emojis: List[Union[str, discord.Emoji]] = self.convert_from_ids(
                    emojiids
                )
                # msgs = automsgdict.get(userid)

                line = f"{' '.join([str(e) for e in emojis])} for {user.display_name}"
                formatted.append(line)
                # await ctx.send(line)

        if formatted:
            formatted = "\n".join(formatted)
            if len(formatted) > 2000:
                pages = list(pagify(formatted))
                await menu(ctx, pages, DEFAULT_CONTROLS)
            else:
                await ctx.send(formatted)
        else:
            await ctx.send("No autoreacts have been set!")

    async def autoreact_handler(self, message: discord.message):
        # don't proc on DMs
        if message.guild is None:
            return

        ctx = await self.bot.get_context(message)
        authorid = str(ctx.author.id)

        async with self.config.guild(
            ctx.guild
        ).autoreact() as autoreactdict, self.config.guild(
            ctx.guild
        ).automsg() as automsgdict:
            has_reacts = authorid in autoreactdict
            has_msg = authorid in automsgdict

            if has_reacts or has_msg:
                if has_reacts:
                    emojis: List[Union[str, discord.Emoji]] = self.convert_from_ids(
                        autoreactdict[authorid]
                    )
                    for emoji in emojis:
                        await message.add_reaction(emoji)
                if has_msg:
                    msg = automsgdict[authorid]
                    await ctx.send(msg, reference=message)

    async def channel_handler(self, message: discord.message):
        # don't proc on DMs
        if message.guild is None:
            return

        ctx = await self.bot.get_context(message)
        user: discord.Member = message.author
        if user.bot:
            return

        channel: Union[
            discord.VoiceChannel, discord.TextChannel, discord.CategoryChannel
        ] = message.channel
        channelid = str(channel.id)

        async with self.config.guild(ctx.guild).channel() as channeldict:
            if channelid not in channeldict:
                return

            emojis: List[Union[str, discord.Emoji]] = self.convert_from_ids(
                channeldict[channelid]
            )
            for emoji in emojis:
                await message.add_reaction(emoji)
