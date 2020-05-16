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
    async def weave(self, ctx, e1, e2, width: int = 5, length: int = 3):
        # <a:name:id>
        guilds = await self.bot.fetch_guilds(limit=150).flatten()
        all_emoji = dict()
        for guild in guilds:
            actual_guild = await self.bot.fetch_guild(guild.id)
            for e in actual_guild.emojis:
                all_emoji[e.id] = e

        e1 = await self.check_emoji(ctx, e1, all_emoji)
        if e1 is None:
            return
        e2 = await self.check_emoji(ctx, e2, all_emoji)
        if e2 is None:
            return

        lines = []
        pair = [e1, e2]
        for _ in range(length):
            line = ""
            index = 0
            for _ in range(width):
                line += str(pair[index % 2])
                index += 1
            pair = pair[::-1]
            lines.append(line)
        msg = "\n".join(lines)

        try:
            await ctx.send(msg)
            await ctx.message.delete()
        except:
            await ctx.send("Message too long!")

    async def check_emoji(self, ctx, emoji, all_emoji):
        if ":" in emoji:
            emoji_id = int(emoji[1:-1].split(":")[-1])
            if emoji_id not in all_emoji:
                await ctx.send("Emoji not from any server I'm in!")
                return None
            else:
                return all_emoji[emoji_id]
        else:
            return emoji
