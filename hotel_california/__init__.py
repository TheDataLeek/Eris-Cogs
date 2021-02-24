from .hotel_california import HotelCalifornia


def setup(bot):
    bot.add_cog(HotelCalifornia(bot))
