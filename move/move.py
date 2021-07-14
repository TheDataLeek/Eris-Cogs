import io
import discord
from redbot.core import commands, Config, checks, bot, utils

BaseCog = getattr(commands, "Cog", object)


class Move(BaseCog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.mod()
    @checks.is_owner()
    async def move(self, ctx, new_channel: discord.TextChannel, *msg_ids: int):
        for msg_id in msg_ids:
            message = await ctx.message.channel.fetch_message(msg_id)

            content = message.content
            attachments = message.attachments

            new_attachments = []
            if attachments:
                for a in attachments:
                    x = io.BytesIO()
                    await a.save(x)

                    x.seek(0)
                    new_attachments.append(
                        discord.File(x, filename=a.filename, spoiler=a.is_spoiler())
                    )

            if len(new_attachments) == 0:
                await new_channel.send(content)
            elif len(new_attachments) == 1:
                await new_channel.send(content, file=new_attachments[0])
            else:
                await new_channel.send(content, files=new_attachments)

            await message.delete()
