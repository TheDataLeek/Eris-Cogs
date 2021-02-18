# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager


BaseCog = getattr(commands, "Cog", object)


class RoleRequest(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot

    @commands.command(pass_context=True)
    async def designate(self, ctx: commands.Context, msg_id: int, role_name: str, emoji: discord.Emoji):
        msg: discord.Message = await ctx.message.channel.fetch_message(msg_id)

        # make sure we have that one
        if emoji.id not in [e.id for e in self.bot.emojis]:
            await ctx.send("Sorry, I don't have that emoji!")
            return

        role: discord.Role = None
        for guild_role in ctx.guild.roles:
            if guild_role.name.lower() == role_name.lower():
                role = guild_role
                break
        else:
            await ctx.send("Sorry, I can't find that role!")
            return

        await msg.add_reaction(emoji)
        # self.bot.add_listener()

