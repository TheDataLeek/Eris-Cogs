from .export_emoji import ExportEmoji


async def setup(bot):
    await bot.add_cog(ExportEmoji(bot))
