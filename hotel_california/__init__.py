from .hotel_california import HotelCalifornia


async def setup(bot):
    await bot.add_cog(HotelCalifornia(bot))
