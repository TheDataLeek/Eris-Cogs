import io
import discord
import qrcode
import random
from redbot.core import commands, bot, checks, data_manager, Config
from redbot.core.utils import embed

BaseCog = getattr(commands, "Cog", object)


class QRGenerator(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot = bot_instance

    @commands.command()
    async def qr(self, ctx: commands.Context):
        """
        Uses library to generate QR codes

        https://github.com/lincolnloop/python-qrcode
        """
        message: discord.Message = ctx.message
        text_to_encode = " ".join(
            word for i, word in enumerate(message.clean_content.split(" ")) if i != 0
        )
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text_to_encode)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="png")
        buf.seek(0)

        await ctx.send(file=discord.File(buf, filename="qr.png"))
