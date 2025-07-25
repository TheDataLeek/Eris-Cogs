import datetime as dt
import re
import pprint

import discord
from redbot.core import commands

import langchain
import langchain.chat_models
import langchain_core
import langchain_core.language_models
import langchain_core.messages
import langgraph
import langgraph.prebuilt

from .base import ChatBase
from ..utils import model_querying
from ..utils import discord_handling


class Agent(ChatBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.bot_instance is not None:
            self.bot_instance.add_listener(self.agent, "on_message")

    async def agent(self, message: discord.Message):
        # Check if the message author is a bot
        if message.author.bot:
            return

        ctx: commands.Context = await self.bot_instance.get_context(message)
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        user: discord.User
        bot_mentioned = False
        for user in message.mentions:
            if user == self.bot_instance.user:
                bot_mentioned = True
        if not bot_mentioned:
            return

        # ignore replies
        message_type: discord.MessageType = message.type
        if message_type == discord.MessageType.reply:
            return

        if self.whois_dictionary is None:
            await self.reset_whois_dictionary()

        prefix: str = await self.get_prefix(ctx)

        try:
            (
                _,
                formatted_query,
                user_names,
            ) = await discord_handling.extract_chat_history_and_format(
                prefix,
                channel,
                message,
                author,
                extract_full_history=True,
                whois_dict=self.whois_dictionary,
            )
        except ValueError as e:
            print(e)
            return

        token = await self.get_openai_token()
        prompt = await self.config.guild(ctx.guild).prompt()
        model_name = await self.config.guild(ctx.guild).model()
        endpoint = await self.config.guild(ctx.guild).endpoint()
        print(f"Using {model_name=} with {endpoint=}")

        if user_names is None:
            user_names = {}
        formatted_usernames = pprint.pformat(user_names)

        today_string = dt.datetime.now().strftime(
            "The date is %A, %B %m, %Y. The time is %I:%M %p %Z"
        )

        system_prefix = {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "text",
                    "text": (
                        "Users have names prefixed by an `@`, however we know the following real names and titles of "
                        f"some of the users involved,\n{formatted_usernames}\nPlease use their names when possible.\n"
                        "Your creator's handle is @erisaurus, and her name is Zoe.\n"
                        "To tag a user, use the format, `<@id>`, but only do this if you don't know their real name.\n"
                        f"{today_string}\n"
                        "Respond in kind, as if you are present and involved. A user has mentioned you and needs your opinion "
                        "on the conversation. Match the tone and style of preceding conversations, do not be overbearing and "
                        "strive to blend in the conversation as closely as possible"
                    ),
                },
            ],
        }
        formatted_query = [system_prefix, *formatted_query]
        model: langchain_core.language_models.BaseChatModel = (
            langchain.chat_models.init_chat_model(
                model_name,
                model_provider="openai",
                api_key=token,
                base_url=endpoint,
            )
        )
        agent = langgraph.prebuilt.create_react_agent(model, [])
        response = agent.invoke({"messages": formatted_query})
        messages: list[langchain_core.messages.BaseMessage] = response["messages"]
        agent_response: str = messages[-1].content
        if isinstance(agent_response, dict):
            agent_response: str = agent_response.get("text")

        # strip multiple newlines
        formatted_response = model_querying.pagify_chat_result(
            re.sub(r"\n{2,}", r"\n", agent_response)
        )

        # pagify for discord and send
        for chunk in formatted_response:
            await ctx.send(chunk)

        # Log the message content to the logged_messages dictionary for the specific channel
        channel_id = message.channel.id
        if channel_id not in self.logged_messages:
            self.logged_messages[
                channel_id
            ] = []  # Initialize the list for this channel

        if (
            len(self.logged_messages[channel_id]) >= 20
        ):  # Keep only the last 20 messages
            self.logged_messages[channel_id].pop(0)  # Remove the oldest message
        self.logged_messages[channel_id].append(message.content)  # Add the new message