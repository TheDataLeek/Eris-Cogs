from .stonks import Stonks


def setup(bot):
    bot.add_cog(Stonks(bot))


if __name__ == '__main__':
    s = Stonks(None)