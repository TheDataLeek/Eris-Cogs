from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)


class Weave(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.all_emoji = None

    async def find_emoji(self):
        if self.all_emoji is None:
            guilds = [guild async for guild in self.bot.fetch_guilds(limit=150)]
            self.all_emoji = dict()
            for guild in guilds:
                actual_guild = await self.bot.fetch_guild(guild.id)
                for e in actual_guild.emojis:
                    self.all_emoji[e.id] = e

    @commands.command()
    async def weave(self, ctx, e1, e2, width: int = 5, length: int = 3):
        """
        Weaves provided emojis in a grid of specified dimensions. Will error if too large.
        """
        # <a:name:id>
        await self.find_emoji()

        e1 = await self.check_emoji(ctx, e1)
        if e1 is None:
            return
        e2 = await self.check_emoji(ctx, e2)
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
        except Exception as e:
            await ctx.send(f"Message too long! {e}")

    async def check_emoji(self, ctx, emoji):
        if ":" in emoji:
            emoji_id = int(emoji[1:-1].split(":")[-1])
            if emoji_id not in self.all_emoji:
                await ctx.send("Emoji not from any server I'm in!")
                return None
            else:
                return self.all_emoji[emoji_id]
        else:
            return emoji
