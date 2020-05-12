from redbot.core import commands, data_manager
import random

BaseCog = getattr(commands, "Cog", object)


class Boo(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        data_dir = data_manager.bundled_data_path(self)
        self.halloween_prefixes = (
            (data_dir / "halloween_prefixes.txt").read_text().split("\n")
        )
        self.thanksgiving_prefixes = (
            (data_dir / "thanksgiving_prefixes.txt").read_text().split("\n")
        )

    def prefix_nick(self, nick, wordlist):
        return random.choice(wordlist) + " " + nick

    async def update_username(self, ctx, wordlist):
        user = ctx.message.author

        original_nick = user.nick or user.display_name

        new_nick = self.prefix_nick(original_nick, wordlist)

        if len(new_nick) >= 32 or len(new_nick.split(" ")) > 3:
            base_nick = new_nick.split(" ")[-1]
            new_nick = self.prefix_nick(base_nick, wordlist)

        new_nick = new_nick.title()

        try:
            await user.edit(nick=new_nick)
        except Exception as e:
            print(e)
            await ctx.send(user.mention + " -> " + new_nick)

    @commands.command()
    async def boo(self, ctx):
        await self.update_username(ctx, wordlist=self.halloween_prefixes)

    @commands.command()
    async def turkey(self, ctx):
        await self.update_username(ctx, wordlist=self.thanksgiving_prefixes)
