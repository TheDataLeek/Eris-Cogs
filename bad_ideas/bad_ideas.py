import discord
from redbot.core import commands, checks
import random
import re
import aiohttp
import io

BaseCog = getattr(commands, "Cog", object)


class BigName(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    async def update_username(self, ctx, user, new_nick):
        try:
            await user.edit(nick=new_nick)
        except Exception as e:
            print(e)
            await ctx.send("Sowwy, I'm unable to do this!")
            return

        if 2 > len(new_nick) > 32:
            await ctx.send("Sowwy, nicks must be between 2 and 32 characters!")
            return

    @commands.command()
    async def big_name(self, ctx, user: discord.Member, *, new_nick: str = ""):
        await self.update_username(ctx, user, new_nick.strip())


class Clone(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.mod()
    async def clone(self, ctx, user: discord.Member):
        new_nick = user.display_name
        my_role = [r for r in user.guild.roles if "snek color" == r.name.lower()]
        if len(my_role) != 1:
            await ctx.send("Error finding role, aborting!")
            return
        my_role = my_role[0]
        avatar = await user.avatar_url_as(format="png", static_format="png").read()
        me = ctx.message.guild.me

        # await ctx.send(file=discord.File(avatar, filename='profile.png'))
        await me.edit(nick=new_nick)
        await self.bot.user.edit(avatar=avatar)
        await my_role.edit(color=user.color)
        await ctx.send("Done")


class FRENSHIP(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_owner()
    async def fren_all(self, ctx):
        await ctx.channel.send("ehhh maybe we'll do this")


class Weave(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weave(self, ctx, width: int, length: int, e1: discord.Emoji, e2: discord.Emoji):
        all_emoji = dict()
        async for guild in self.bot.fetch_guilds():
            for e in guild.emojis:
                all_emoji[e.id] = e

        if e1.id not in all_emoji or e2.id not in all_emoji:
            await ctx.send("Emoji not from this server!")
            return

        if width * length > 25:
            await ctx.send("Message too long!")
            return

        lines = []
        pair = [e1, e2]
        for _ in range(length):
            lines.append(width * ("{}{}".format(*pair)))
            pair = pair[::-1]
        msg = '\n'.join(lines)

        await ctx.send(msg)

