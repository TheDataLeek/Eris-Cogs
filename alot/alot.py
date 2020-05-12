import io
import discord
from redbot.core import commands, data_manager, Config, checks
from functools import reduce


BaseCog = getattr(commands, "Cog", object)


class Alot(BaseCog):
    def __init__(self, bot):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=928487392010)

        default_global = {
            'guild_list': [],
        }
        default_guild = {
            'channel_whitelist': ['general', 'bot-chat'],
            'channel_blacklist': ['news'],
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)

        data_dir = data_manager.bundled_data_path(self)
        self.alot = (data_dir / 'ALOT.png').read_bytes()

        self.bot.add_listener(self.alot_of_patience, "on_message")

    @commands.command()
    @checks.is_owner()
    async def add_server(self, ctx, server_name):
        async with self.config.guild_list() as guild_list:
            guild_list.append(server_name)

    @commands.command()
    @checks.is_owner()
    async def remove_server(self, ctx, server_name):
        async with self.config.guild_list() as guild_list:
            try:
                guild_list.remove(server_name)
            except ValueError:
                await ctx.send('Server was not in list!')

    @commands.command()
    @checks.mod()
    async def whitelist_channel(self, channel):
        pass

    async def alot_of_patience(self, message):
        server_list = await self.config.guild_list()
        if message.guild is None or message.guild.name.lower() not in server_list:
            return

        clean_message = message.clean_content.lower()
        # MM: Added so list instead of string
        message_split = clean_message.split(" ")

        # BLACKLIST CHANNELS
        blacklist = [
            "news",
            "rpg",
            "events",
            "recommends",
            "politisophy",
            "eyebleach",
            "weeb-lyfe",
            "out-of-context",
            "jokes",
            "anime-club",
        ]

        message_channel = message.channel.name.lower()

        if "alot" not in clean_message:
            return

        if (
                # DO NOT RESPOND TO SELF MESSAGES
                (self.bot.user.id == message.author.id or message.content.startswith("."))
                or (message.channel.name is None)
                or (
                reduce(
                    lambda acc, n: acc or (n == message_channel), blacklist, False
                )
        )
                or ("thank" in clean_message)
                or ("http" in clean_message)
        ):
            return

        ctx = await self.bot.get_context(message)

        await ctx.send(file=discord.File(io.BytesIO(self.alot), filename='alot.png'))
