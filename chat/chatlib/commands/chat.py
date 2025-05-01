import discord
from redbot.core import commands

from . import discord_handling, model_querying, ChatBase


class ChatCommands(ChatBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot.add_listener(self.contextual_chat_handler, "on_message")

    @commands.command()
    async def chat(self, ctx: commands.Context) -> None:
        """
        Engages in a chat conversation using a custom GPT-4 prompt and create an active thread if not already in one.
        Usage:
        [p]chat <your_message>
        Example:
        [p]chat How are you doing today?
        Upon execution, the bot will process the chat history and the provided message, then respond within the same
        thread.
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        prefix: str = await self.get_prefix(ctx)
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        if self.whois_dictionary is None:
            await self.reset_whois_dictionary()
        try:
            (
                thread_name,
                formatted_query,
                user_names,
            ) = await discord_handling.extract_chat_history_and_format(
                prefix, channel, message, author, whois_dict=self.whois_dictionary
            )
        except ValueError:
            await ctx.send("Something went wrong!")
            return
        token = await self.get_openai_token()
        prompt = await self.config.guild(ctx.guild).prompt()
        model = await self.config.guild(ctx.guild).model()
        response = await model_querying.query_text_model(
            token, prompt, formatted_query, model=model, user_names=user_names
        )
        await discord_handling.send_response(response, message, channel, thread_name)

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
        model = await self.config.guild(ctx.guild).model()
        response = await model_querying.query_text_model(
            token,
            prompt,
            formatted_query,
            model=model,
            user_names=user_names,
            contextual_prompt=(
                "Respond in kind, as if you are present and involved. A user has mentioned you and needs your opinion "
                "on the conversation. Match the tone and style of preceding conversations, do not be overbearing and "
                "strive to blend in the conversation as closely as possible"
            ),
        )
        for page in response:
            await channel.send(page)

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
