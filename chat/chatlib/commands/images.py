from __future__ import annotations

import discord
from redbot.core import commands

from chat.chatlib import discord_handling, model_querying
from .base import ChatBase


class ImageCommands(ChatBase):
    @commands.command()
    async def image(self, ctx: commands.Context):
        """
        Generates an image based on the user's prompt using the DALL-E 3 model.
        Usage:
        [p]image <your_prompt>
        Example:
        [p]image A cat riding a skateboard in space
        Upon execution, the bot will generate an image matching the description and send it in the chat.
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        await self._image(channel, message, model="dall-e-3")

    @commands.command()
    async def images(self, ctx: commands.Context):
        """
        Generates multiple images based on the user's prompt using the DALL-E 2 model.
        Usage:
        [p]images <your_prompt>
        Example:
        [p]images A beautiful sunset over the mountains
        Upon execution, the bot will generate four images matching the description and send them in the chat.
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        await self._image(channel, message, n_images=4, model="dall-e-2")

    async def _image(
        self,
        channel: discord.abc.Messageable,
        message: discord,
        n_images=1,
        model: str = None,
    ):
        attachments: list[discord.Attachment] = [
            m for m in message.attachments if m.width
        ]
        attachment = None
        if len(attachments) > 0:
            attachment: discord.Attachment = attachments[0]

        prompt_words = [w for i, w in enumerate(message.content.split(" ")) if i != 0]
        prompt: str = " ".join(prompt_words)
        thread_name = " ".join(prompt_words[:5]) + " image"
        token = await self.get_openai_token()
        try:
            response = await model_querying.query_image_model(
                token, prompt, attachment, n_images=n_images, model=model
            )
        except ValueError:
            await channel.send("Something went wrong!")
            return
        await discord_handling.send_response(response, message, channel, thread_name)

    @commands.command()
    async def expand(self, ctx: commands.Context):
        """
        Expands an image based on the user's prompt using an AI model.
        Usage:
        [p]expand <your_prompt>
        Example:
        [p]expand Make this forest scene extend to the left with more trees and a river
        Notes:
        - The user must attach an image or reference one in their message.
        - The bot will notify the user if no image is provided before attempting the expansion.
        Upon execution, the bot will generate an expanded version of the image and send it in the chat.
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        attachment = None
        attachments: list[discord.Attachment] = [
            m for m in message.attachments if m.width
        ]
        if message.reference:
            referenced: discord.MessageReference = message.reference
            referenced_message: discord.Message = await channel.fetch_message(
                referenced.message_id
            )
            attachments += [m for m in referenced_message.attachments if m.width]
        if len(attachments) > 0:
            attachment: discord.Attachment = attachments[0]
        else:
            await ctx.send(f"Please provide an image to expand!")
            return

        prompt_words = [w for i, w in enumerate(message.content.split(" ")) if i != 0]
        prompt: str = " ".join(prompt_words)
        thread_name = " ".join(prompt_words[:5]) + " image"
        token = await self.get_openai_token()
        try:
            response = await model_querying.query_image_model(
                token, prompt, attachment, image_expansion=True
            )
        except ValueError:
            await ctx.send("Something went wrong!")
            return
        await discord_handling.send_response(response, message, channel, thread_name)
