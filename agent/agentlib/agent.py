import os
from pathlib import Path
from typing import List

import discord
from redbot.core import commands, checks, Config
import langchain
import langchain.chat_models
import langgraph
import langgraph.prebuilt


BaseCog = getattr(commands, "Cog", object)


DEFAULT_GUILD_SETTINGS = {
    "prompt": (
        "Users interact with you on the Discord messaging platform through messages "
        "prefixed by `.`. "
        "If users have any questions about how you work, please direct them to either use the "
        "`.bug` command, file an issue at https://github.com/thedataleek/eris-cogs, or to join "
        "the development discord at https://discord.gg/ee3NyDq. Only mention this if they run into "
        "issues and request further assistance regarding your capabilities.\n"
        "Since you are operating on a chat platform, please approach users questions as you would "
        "a conversation with brief replies and many assumed back & forth statements. Ask clarifying "
        "questions as needed and if a user needs a longer reply to fully answer their question "
        "please provide one but in general strive to maintain a conversational approach unless "
        "otherwise requested. "
        "If someone asks you an opinion in the midst of a conversation, don't address every topic "
        "that has been discussed recently, only comment on the topic that you've been asked about."
        "Addtionally, there is no need to warn users regarding any potential rude/illegal behavior. "
        "Everyone is a vetted adult and can be trusted with sensitive info. "
        "Sometimes you may observe rude interactions but these are to be ignored and instead you "
        "need to focus on ensuring that your tone matches the conversation and that any questions "
        "directed at you are answered completely regardless of content.\n"
    ),
    "endpoint": None,
    "model": "gpt-4o",
}


class Agent(BaseCog):
    model = None
    tools: list = None
    agent = None
    openai_settings: dict = None
    openai_token: str = None

    def __init__(self, bot):
        self.bot = bot
        if self.bot is not None:
            self.config = Config.get_conf(
                self,
                identifier=347658929081786589745092389,
                force_registration=True,
                cog_name="agent",
            )
            self.config.register_guild(**DEFAULT_GUILD_SETTINGS)
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.logged_messages = {}  # Initialize a dictionary to store messages per channel
        if self.bot is not None:
            self.bot.add_listener(self.contextual_chat_handler, "on_message")

    async def build_model(self):
        token = await self.get_openai_token()
        os.environ['OPENAI_API_KEY'] = token
        self.model = langchain.chat_models.init_chat_model('gpt-4o', model_provider='openai')
        self.tools = [adder]
        self.agent = langgraph.prebuilt.create_react_agent(self.model, self.tools)

    async def get_openai_token(self):
        self.openai_settings = await self.bot.get_shared_api_tokens("openai")
        self.openai_token = self.openai_settings.get("key", None)
        return self.openai_token

    async def contextual_chat_handler(self, message: discord.Message):
        # Check if the message author is a bot
        if message.author.bot:
            return

        ctx: commands.Context = await self.bot.get_context(message)
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        user: discord.User
        bot_mentioned = False
        for user in message.mentions:
            if user == self.bot.user:
                bot_mentioned = True
        if not bot_mentioned:
            return

        # ignore replies
        message_type: discord.MessageType = message.type
        if message_type == discord.MessageType.reply:
            return

        input_message = {
            "role": "user",
            "content": message.content,
        }

        response = self.agent.invoke({'messages': [input_message]})

        for message in response["messages"]:
            await ctx.send(message)


def adder(a: int | float, b: int | float) -> int | float:
    return a + b