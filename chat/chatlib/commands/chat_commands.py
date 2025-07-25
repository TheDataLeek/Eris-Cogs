import discord
from redbot.core import commands

from .base import ChatBase
from rich import print
import os
print(os.getcwd())
import sys
print(sys.path)
from .. import model_querying, discord_handling


class ChatCommands(ChatBase):
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
        endpoint = await self.config.guild(ctx.guild).endpoint()
        print(f"Using {model=} with {endpoint=}")
        response = await model_querying.query_text_model(
            token,
            prompt,
            formatted_query,
            model=model,
            user_names=user_names,
            endpoint=endpoint,
        )
        await discord_handling.send_response(response, message, channel, thread_name)
