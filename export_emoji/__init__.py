from .export_emoji import ExportEmoji


def setup(bot):
    bot.add_cog(ExportEmoji(bot))
