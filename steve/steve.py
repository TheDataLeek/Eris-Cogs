import random
import re
import discord
from redbot.core import commands, data_manager, Config, checks, bot

from .eris_event_lib import ErisEventMixin

BaseCog = getattr(commands, "Cog", object)

RETYPE = type(re.compile("a"))


class Steve(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot = bot_instance

        self.asking_about_steve = [
            "where stev",
            "where is stev",
            "where's stev",
            "wheres stev",
        ]
        self.links = [
            "https://cdn.discordapp.com/attachments/345659033971326996/367200478993580042/Steve1.png",
            "https://cdn.discordapp.com/attachments/345659033971326996/367200480276905994/Steve2.png",
            "https://cdn.discordapp.com/attachments/345659033971326996/367200481589854211/Steve3.png",
            "https://cdn.discordapp.com/attachments/345659033971326996/367200483426697216/Steve4.png",
            "https://cdn.discordapp.com/attachments/345659033971326996/367200484290854913/Steve5.png",
        ]
        self.bot.add_listener(self.steve, "on_message")

    async def steve(self, message: discord.Message):
        if random.random() <= 0.5:
            return
        for s in self.asking_about_steve:
            if s in message.clean_content.lower():
                break
        else:
            return

        ctx = await self.bot.get_context(message)

        msg = " ".join(self.links)
        if random.random() <= 0.1:
            msg = " ".join(random.sample(self.links, len(self.links)))
        await ctx.send(msg)

        await self.log_last_message(ctx, message)
