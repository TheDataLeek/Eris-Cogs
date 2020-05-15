import random
import discord
from redbot.core import commands, data_manager, Config, checks, bot


BaseCog = getattr(commands, "Cog", object)


class Spoop(BaseCog):
    def __init__(self, bot_instance):
        self.bot: bot = bot_instance
        self.whois = self.bot.get_cog("WhoIs")
        self.event_config = self.bot.get_cog('EventConfig')
        if self.event_config is None:
            raise FileNotFoundError('Need to install event_config')

        data_dir = data_manager.bundled_data_path(self)
        self.yandere_quotes = (data_dir / "yandere_quotes.txt").read_text().split('\n')

        self.bot.add_listener(self.randomly_spoop, "on_message")

    async def randomly_spoop(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        allowed: bool = await self.event_config.allowed(ctx, message)
        randomly_allowed: bool = random.random() <= 0.01
        if not allowed or not randomly_allowed:
            return

        author: discord.Member = message.author
        realname = author.mention
        if self.whois is not None:
            realname = self.whois.convert_realname(await self.whois.get_realname(ctx, str(author.id)))

        new_message = random.choice(self.yandere_quotes)

        new_message = " ".join(x.format(realname) for x in new_message.split(" "))
        await author.send(new_message)

        await self.event_config.log_last_message(ctx, message)

    @commands.command()
    @checks.mod()
    async def spoop(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.message.author.send("Stop being such a fuckup")
            await ctx.message.delete()
            return

        realname = user.mention
        if self.whois is not None:
            realname = self.whois.convert_realname(await self.whois.get_realname(ctx, str(user.id)))

        new_message = random.choice(self.yandere_quotes)

        new_message = " ".join(x.format(realname) for x in new_message.split(" "))
        await user.send(new_message)
        await ctx.message.delete()
