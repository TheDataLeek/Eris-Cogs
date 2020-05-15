import discord
from redbot.core import commands, bot


BaseCog = getattr(commands, "Cog", object)


class Sudo(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

        self.whois = self.bot.get_cog("WhoIs")

        self.event_config = self.bot.get_cog('EventConfig')
        if self.event_config is None:
            raise FileNotFoundError('Need to install event_config')

        self.bot.add_listener(self.no_sudo, "on_message")

    async def no_sudo(self, message: discord.Message):
        ctx = await self.bot.get_context(message)

        allowed: bool = await self.event_config.allowed(ctx, message)
        keyword_in_message: bool = 'sudo' in message.clean_content

        if not allowed or not keyword_in_message:
            return

        author: discord.Member = message.author
        realname = author.mention
        if self.whois is not None:
            realname = self.whois.convert_realname(await self.whois.get_realname(ctx, str(author.id)))

        await message.channel.send("{} is not in the sudoers file. This incident will be reported.".format(realname))

        await self.event_config.log_last_message(ctx, message)

