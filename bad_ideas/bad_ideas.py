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
    @checks.is_owner()
    async def clone(self, ctx, user: discord.Member):
        new_nick = user.display_name
        avatar = str(user.avatar_url)
        me = ctx.message.guild.me

        async with aiohttp.ClientSession() as sesh:
            async with sesh.get(avatar) as resp:
                data = await resp.read()

                await ctx.send(file=discord.File(data))
                await me.edit(nick=new_nick, avatar=data)

        await ctx.send("Done")
