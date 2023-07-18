from typing import List, Dict, Union

from redbot.core import commands
import discord
import openai

BaseCog = getattr(commands, "Cog", object)


class Chat(BaseCog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_settings = None
        self.openai_token = None

    async def get_openai_token(self):
        self.openai_settings = await self.bot.get_shared_api_tokens("openai")
        self.openai_token = self.openai_settings.get("key", None)
        return self.openai_token

    @commands.command()
    async def chat(self, ctx: commands.Context, *query: str):
        if not query:
            return

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        if isinstance(channel, discord.TextChannel):
            openai_query = [{"role": "user", "content": " ".join(query)}]
        elif isinstance(channel, discord.Thread):
            history = [message async for message in channel.history(limit=100)]
            history = [
                {
                    "role": 'system' if message.author.bot else 'user',
                    'content': ' '.join(w for w in message.clean_content.split(' ') if w != '.chat')  # todo: prefix
                }
            ]
            openai_query = history
        else:
            return

        openai.api_key = await self.get_openai_token()
        chat_completion: Dict = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                             messages=openai_query,
                                                             temperature=1.5)
        try:
            response = chat_completion['choices'][0]['message']['content']
            thread: discord.Thread = await message.create_thread(name=openai_query[:15] + '...')
            await thread.send(response)
        except Exception as e:
            raise
