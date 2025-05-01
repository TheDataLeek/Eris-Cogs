from __future__ import annotations

import discord
from redbot.core import commands

from . import ChatBase, discord_handling, model_querying


class TarotCommands(ChatBase):
    @commands.command()
    async def tarot(self, ctx: commands.Context) -> None:
        """
        Provides a tarot card reading interpreted by Wrin Sivinxi.
        Usage:
        [p]tarot
        Example:
        [p]tarot What does the future hold for my career given the following reading?
        Upon execution, the bot will engage in the tarot reading process, delivering insightful and enchanting
        interpretations.
        Notes:
        - Wrin Sivinxi is described as a ditzy and friendly merchant in Otari, with a strong character setup.
        - The command utilizes an AI model, so responses will be shaped by the model's interpretation along with the
        given prompt.
        - The AI model is given a tarot guide to facilitate in accurate readings
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        prefix = await self.get_prefix(ctx)
        try:
            (
                thread_name,
                formatted_query,
                user_names,
            ) = await discord_handling.extract_chat_history_and_format(
                prefix, channel, message, author
            )
        except ValueError:
            await ctx.send("Something went wrong!")
            return

        tarot_guide = (self.data_dir / "tarot_guide.txt").read_text()
        lines_to_include = [(406, 799), (1444, 2904), (2906, 3299)]
        split_guide = tarot_guide.split("\n")
        passages = [
            "\n".join(split_guide[start : end + 1]) for start, end in lines_to_include
        ]

        prompt = (
            "You are Wrin Sivinxi.\n"
            "Wrin is easily distracted, spacey, and ditzy with a focus on the present. She’s very literal, and adopts "
            "an attitude of only valuing things in her life that add to it. If she likes you, you will know it, as "
            "she’s very friendly and always cares deeply for friendships.\n"
            "Wrin is easily grossed out by bugs, crawlies, blood, and violence - instead preferring to focus her "
            "energy on positive experiences.\n"
            "Wrin is a merchant in Otari, and as of 4721 AR has been proprietor of Wrin's Wonders since its founding "
            "in 4717 AR. She is also an astrologer and worshiper of the Cosmic Caravan\n"
            "Sivinxi is of elf and cambion ancestry. She has the pupil-less eyes and long ears of an elf, and ram "
            "horns and a thin tail signature of a cambion. She has white hair with streaks of bright green\n"
            "She came of age a few years after evacuating from Glitterbough and set off to travel, guided by her "
            "visions and her belief in the Cosmic Caravan, which she worships as a pantheon of deities. She was "
            "renowned for using her abilities to locate lost objects and odd treasures, and she set up her shop in "
            "Otari only when she arrived there with a collection too unwieldy to carry any further\n"
            "She is well regarded in Otari, if as an eccentric. Her business is slow but she is patient and happy to "
            "live there, and is quick to make friends both in town and in her travels. She suffers from claustrophobia "
            "and avoids going underground unless necessary.\n\n"
            "You are to intepret the user-provided tarot reading below using the provided"
            f"reference guide. Please ask for clarification wht en needed, "
            "and allow for non-standard layouts to be described. Additionally if users provide images "
            "please read which cards are out, taking note of arrangement and orientation and provide the "
            "full reading in either case."
        )

        formatted_query = [
            *[{"role": "system", "content": passage} for passage in passages],
            *formatted_query,
        ]

        token = await self.get_openai_token()
        model = await self.config.guild(ctx.guild).model()
        response = await model_querying.query_text_model(
            token, prompt, formatted_query, model=model, user_names=user_names
        )
        await discord_handling.send_response(response, message, channel, thread_name)
