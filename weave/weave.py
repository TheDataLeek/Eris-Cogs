from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

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