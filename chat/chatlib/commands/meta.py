from __future__ import annotations

import discord
from redbot.core import commands, checks
from redbot.core.utils.views import ConfirmView

from .base import ChatBase


class MetaCommands(ChatBase):
    @commands.command()
    @checks.mod()
    async def setprompt(self, ctx):
        """
        Sets a custom prompt for this server's GPT-4 based interactions.
        Usage:
        [p]setprompt <prompt_text> or attach a file with the prompt.
        Example:
        [p]setprompt Welcome to our server! How can I assist you today?
        After running the command, the bot will confirm with a "Done" message.
        """
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return

        # Check for attached files
        if message.attachments:
            attachment = message.attachments[0]
            # Ensure the file is a text file
            if attachment.filename.endswith(".txt"):
                file_content = await attachment.read()
                contents = file_content.decode("utf-8")  # Decode the file content
            else:
                await ctx.send("Please attach a valid text file (.txt).")
                return
        else:
            contents = " ".join(message.clean_content.split(" ")[1:])  # skip command

        await self.config.guild(ctx.guild).prompt.set(contents)
        await ctx.send("Done")

    @commands.command()
    @checks.mod()
    async def setmodel(self, ctx):
        """
        Sets a custom model for this server's GPT based interactions. Current options are found here -
        https://platform.openai.com/docs/models/model-endpoint-compatibility

        Default is `gpt-4o`.

        Usage:
        [p]setmodel <model name>
        Example:
        [p]setmodel gpt-4o
        """
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        contents = " ".join(message.clean_content.split(" ")[1:])  # skip command
        await self.config.guild(ctx.guild).model.set(contents)
        await ctx.send("Done")

    @commands.command()
    @checks.mod()
    async def setendpoint(self, ctx):
        """
        Sets a custom endpoint for this server's GPT based interactions. Current options are found here -

        Usage:
        [p]setendpoint <model name>
        """
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        contents = " ".join(message.clean_content.split(" ")[1:])  # skip command
        await self.config.guild(ctx.guild).endpoint.set(contents)
        await ctx.send("Done")

    @commands.command()
    async def showprompt(self, ctx):
        """
        Displays the current custom GPT-4 prompt for this server.
        Usage:
        [p]showprompt
        Example:
        [p]showprompt
        Upon execution, the bot will send the current prompt in the chat.
        """
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        prompt = await self.config.guild(ctx.guild).prompt()

        # Split the prompt into chunks of 2000 characters or less
        for i in range(0, len(prompt), 2000):
            await ctx.send(prompt[i : i + 2000])  # Send each chunk

    async def reset_whois_dictionary(self):
        self.whois = self.bot_instance.get_cog("WhoIs")
        if self.whois is None:
            self.whois_dictionary = {}
            return

        whois_config = self.whois.config

        guilds: list[discord.Guild] = self.bot_instance.guilds
        final_dict = {}
        for guild in guilds:
            guild_name = guild.name
            final_dict[guild_name] = (
                await whois_config.guild(guild).whois_dict()
            ) or dict()

        self.whois_dictionary = final_dict

    @commands.command()
    @checks.mod()
    async def rewind(self, ctx: commands.Context) -> None:
        """
        Rewinds the chat in an active thread by removing the bot's latest responses and the associated user input.
        Usage:
        [p]rewind
        Note:
        The command can only be used within an active thread. If used elsewhere, the bot will notify the user that it
        requires an active thread.
        Example:
        [p]rewind
        The bot will delete the necessary messages and confirm by deleting the user's command message as well.
        """
        prefix = await self.get_prefix(ctx)

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        not_in_a_guild = message.guild is None
        not_in_a_thread = not isinstance(message.channel, discord.Thread)
        if not_in_a_guild or not_in_a_thread:
            await ctx.send(
                "Rewinding can only be used in an active thread in a guild! Please ask a question first using [p]chat"
            )
            return

        view = ConfirmView(ctx.author, disable_buttons=True)
        view.message = await ctx.send(
            "Are you sure you want to rewind? Make sure you copy your original prompt "
            "before continuing (it's gonna get deleted too)!",
            view=view,
        )
        await view.wait()
        if not view.result:
            return

        found_bot_response = False
        found_last_bot_response = False
        found_chat_input = False
        async for thread_message in channel.history(limit=100, oldest_first=False):
            try:
                if (not found_chat_input) and thread_message.clean_content.startswith(
                    f"{prefix}chat"
                ):
                    await thread_message.delete()
                    found_chat_input = True

                if thread_message.author.bot:
                    await thread_message.delete()
                    found_bot_response = True
                elif found_bot_response:
                    found_last_bot_response = True

                if found_chat_input and found_bot_response and found_last_bot_response:
                    break
            except Exception as e:
                break

        await message.delete()

    @commands.command()
    @checks.mod()  # add check for mods
    async def lastmessages(self, ctx: commands.Context):
        """
        Displays the last 20 messages sent to ChatGPT from this channel.
        Usage:
        [p]show_logged_messages
        Example:
        [p]show_logged_messages
        Upon execution, the bot will send the logged messages in the chat.
        """
        channel_id = ctx.channel.id
        if (
            channel_id not in self.logged_messages
            or not self.logged_messages[channel_id]
        ):
            await ctx.send("No messages logged yet.")
            return

        # Send the logged messages for this specific channel
        for msg in self.logged_messages[channel_id]:
            await ctx.send(msg)
