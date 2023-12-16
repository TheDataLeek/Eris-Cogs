from .generate_qrcode import QRGenerator


async def setup(bot):
    await bot.add_cog(QRGenerator(bot))
