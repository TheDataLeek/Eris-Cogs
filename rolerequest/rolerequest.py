# stdlib
from pprint import pprint as pp

# third party
import discord
from discord import utils
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

        async def add_role_to_user(reaction: discord.RawReactionActionEvent):
            guild: discord.Guild = utils.get(self.bot.guilds, id=reaction.guild_id)
            hooks = await self.config.guild(guild).hooks()
            message_id = str(reaction.message_id)
            if message_id not in hooks:
                return

            emoji_id = str(reaction.emoji.id)
            if emoji_id not in hooks[message_id]:
                return

            role: discord.Role = None
            for guild_role in guild.roles:
                if guild_role.name.lower() == hooks[message_id][emoji_id].lower():
                    role = guild_role
                    break
            else:
                return

            user_id = reaction.user_id
            user: discord.Member = await guild.fetch_member(user_id)

            if not user.bot:
                # print(f"Adding {role} to {user} via {emoji_id}")
                await user.add_roles(role)

        async def remove_role_from_user(reaction: discord.RawReactionActionEvent):
            guild: discord.Guild = utils.get(self.bot.guilds, id=reaction.guild_id)
            hooks = await self.config.guild(guild).hooks()
            message_id = str(reaction.message_id)
            if message_id not in hooks:
                return

            emoji_id = str(reaction.emoji.id)
            if emoji_id not in hooks[message_id]:
                return

            role: discord.Role = None
            for guild_role in guild.roles:
                if guild_role.name.lower() == hooks[message_id][emoji_id].lower():
                    role = guild_role
                    break
            else:
                return

            user_id = reaction.user_id
            user: discord.Member = await guild.fetch_member(user_id)
            if not user.bot:
                await user.remove_roles(role)

        bot.add_listener(add_role_to_user, "on_raw_reaction_add")
        bot.add_listener(remove_role_from_user, "on_raw_reaction_remove")

    @commands.command(pass_context=True)
    @checks.mod()
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
        emoji_id = str(emoji.id)
        msg_id = str(msg_id)
        if msg_id in hooks:
            hooks[msg_id][emoji_id] = role_name
        else:
            hooks[msg_id] = {emoji_id: role_name}
        await self.config.guild(ctx.guild).hooks.set(hooks)

    @commands.command(pass_context=True)
    @checks.mod()
    async def clear_message(self, ctx: commands.Context, msg_id: str):
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

