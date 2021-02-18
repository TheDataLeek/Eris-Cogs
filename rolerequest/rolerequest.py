# stdlib
from time import sleep
from random import choice as randchoice
import random

# third party
import discord
from redbot.core import commands, data_manager, Config, checks


BaseCog = getattr(commands, "Cog", object)


class RoleRequest(BaseCog):
    def __init__(self, bot: commands.Cog):
        self.bot: commands.Cog = bot

        self.config = Config.get_conf(
            None, identifier=23488191910303, cog_name="rolerequest"
        )
        default_global = {}
        default_guild = {"hooks": {}}
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        async def add_role_to_user(reaction: discord.RawReactionActionEvent, user: discord.Member):
            hooks = await self.config.guild(reaction.guild_id).hooks()
            if reaction.message_id not in hooks:
                return

            message = reaction.message
            emoji_id = reaction.emoji_id

            if emoji_id not in hooks[reaction.message_id]:
                return

            role: discord.Role = None
            for guild_role in message.guild.roles:
                if guild_role.name.lower() == hooks[reaction.message_id][emoji_id].lower():
                    role = guild_role
                    break
            else:
                return

            await user.add_roles(role)

        async def remove_role_from_user(reaction: discord.RawReactionActionEvent, user: discord.Member):
            hooks = await self.config.guild(reaction.guild_id).hooks()
            if reaction.message_id not in hooks:
                return

        bot.add_listener(add_role_to_user, "on_reaction_add")
        bot.add_listener(remove_role_from_user, "on_reaction_remove")

    @commands.command(pass_context=True)
    async def designate(
        self, ctx: commands.Context, msg_id: int, role_name: str, emoji: discord.Emoji
    ):
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

        hooks = await self.config.guild(ctx.guild).hooks()
        msg_id = str(msg_id)
        emoji_id = str(emoji.id)
        if msg_id in hooks:
            hooks[msg_id][emoji_id] = role_name
        else:
            hooks[msg_id] = {emoji_id: role_name}
        await self.config.guild(ctx.guild).hooks.set(hooks)

    @commands.command(pass_context=True)
    async def clear_message(self, ctx: commands.Context, msg_id: int):
        msg: discord.Message = await ctx.message.channel.fetch_message(msg_id)
        hooks = await self.config.guild(ctx.guild).hooks()
        if msg_id not in hooks:
            return

        del hooks[msg_id]
        await self.config.guild(ctx.guild).hooks.set(hooks)

        await msg.clear_reactions()

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def clear_all_data(self, ctx):
        await self.config.guild(ctx.guild).hooks.set({})
