from __future__ import annotations

import discord
from redbot.core import commands, data_manager, bot, Config, checks
from redbot.core.bot import Red
import asyncio  #needed for user id stuff for cooldowns

from .chatlib import discord_handling, model_querying

BaseCog = getattr(commands, "Cog", object)


class Chat(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot: Red = bot_instance
        self.openai_settings = None
        self.openai_token = None
        self.mention_cooldowns = {}  # initialises mention_cooldowns stuff here
        self.config = Config.get_conf(
            self,
            identifier=23458972349810010102367456567347810101,
            force_registration=True,
            cog_name="chat",
        )
        self.exempt_users = []  # List to store exempted user IDs
        self.load_exempt_users()  # Load exempt users from config

        default_guild = {
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
            "cooldown": 10,  # default cooldown in seconds
            "exempt_users": []  # Initialize exempt users as an empty list
        }
        self.config.register_guild(**default_guild)
        self.data_dir = data_manager.bundled_data_path(self)
        self.whois_dictionary = None
        self.bot.add_listener(self.contextual_chat_handler, "on_message")

    async def load_exempt_users(self):
        """Load exempt users from the configuration."""
        self.exempt_users = await self.config.guild().exempt_users() or []
        print(f"Loaded exempt users: {self.exempt_users}")  # Debug statement

    @commands.command()
    @checks.mod()
    async def setprompt(self, ctx):
        """
        Sets a custom prompt for this server's GPT-4 based interactions.
        Usage:
        [p]setprompt <prompt_text>
        Example:
        [p]setprompt Welcome to our server! How can I assist you today?
        After running the command, the bot will confirm with a "Done" message.
        """
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        contents = " ".join(message.clean_content.split(" ")[1:])  # skip command
        await self.config.guild(ctx.guild).prompt.set(contents)

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
            await ctx.send(prompt[i:i + 2000])  # Send each chunk

    @commands.command()
    @checks.mod()
    async def setcooldown(self, ctx, seconds: int):
        """
        Sets a cooldown period for the chat commands in this server.
        Usage:
        [p]setcooldown <seconds>
        Example:
        [p]setcooldown 30
        After running the command, the bot will confirm with a "Cooldown set to <seconds> seconds" message.
        """
        message: discord.Message = ctx.message
        if message.guild is None:
            await ctx.send("Can only run in a text channel in a server, not a DM!")
            return
        await self.config.guild(ctx.guild).cooldown.set(seconds)
        await ctx.send(f"Cooldown set to {seconds} seconds.")

    @commands.command()
    @checks.mod()
    async def exemptcooldown(self, ctx, *exempted_users: discord.User):
        """
        Exempts specified users from the cooldown period.
        Usage:
        [p]exemptcooldown @User1 @User2
        Example:
        [p]exemptcooldown @User1 @User2
        After running the command, the bot will confirm the exempted users.
        """
        for user in exempted_users:
            if user.id not in self.exempt_users:
                self.exempt_users.append(user.id)  # Add exempted user IDs

        # Save to config using the guild context
        await self.config.guild(ctx.guild).exempt_users.set(self.exempt_users)  
        await ctx.send(f"Exempted users: {', '.join(str(user.id) for user in exempted_users)}")



    @commands.command()
    @checks.mod()
    async def showexemptusers(self, ctx):
        """
        Displays the current exempted users from the cooldown period.
        Usage:
        [p]showexemptusers
        Example:
        [p]showexemptusers
        Upon execution, the bot will send the list of exempted users in the chat.
        """
        if not self.exempt_users:
            await ctx.send("There are currently no exempted users.")
        else:
            exempted_user_ids = ', '.join(str(user_id) for user_id in self.exempt_users)
            await ctx.send(f"Exempted users: {exempted_user_ids}")

    async def reset_whois_dictionary(self):
        self.whois = self.bot.get_cog("WhoIs")
        if self.whois is None:
            self.whois_dictionary = {}
            return

        whois_config = self.whois.config

        guilds: list[discord.Guild] = self.bot.guilds
        final_dict = {}
        for guild in guilds:
            guild_name = guild.name
            final_dict[guild_name] = (await whois_config.guild(guild).whois_dict()) or dict()

        self.whois_dictionary = final_dict

    async def contextual_chat_handler(self, message: discord.Message):
        ctx: commands.Context = await self.bot.get_context(message)
        author: discord.Member = message.author

        # Debug: Print the author ID and exempt users
        print(f"Author ID: {author.id}, Exempt Users: {self.exempt_users}")

        # Check if the user is exempt from cooldown
        if author.id in self.exempt_users:
            print(f"User {author.id} is exempt from cooldown.")
            return  # Skip cooldown check for exempted users

        # Check for cooldown
        current_time = discord.utils.utcnow().timestamp()
        cooldown_duration = await self.config.guild(ctx.guild).cooldown()

        if author.id in self.mention_cooldowns:
            last_mentioned_time = self.mention_cooldowns[author.id]
            if current_time - last_mentioned_time < cooldown_duration:
                await ctx.send("You're on cooldown for mentioning the bot. Please wait a bit.")
                return

        # Check if the bot is mentioned
        if self.bot.user in message.mentions:
            print(f"Bot mentioned by {author.id}.")
            self.mention_cooldowns[author.id] = current_time  # Update the timestamp
        else:
            print("Bot was not mentioned.")
            return  # Exit if the bot was not mentioned

        # Proceed with handling the message if the bot was mentioned
        if self.whois_dictionary is None:
            await self.reset_whois_dictionary()

        prefix: str = await self.get_prefix(ctx)
        try:
            (_, formatted_query, user_names) = await discord_handling.extract_chat_history_and_format(
                prefix, ctx.channel, message, author, extract_full_history=True, whois_dict=self.whois_dictionary
            )
        except ValueError as e:
            print(e)
            return

        token = await self.get_openai_token()
        prompt = await self.config.guild(ctx.guild).prompt()
        response = await model_querying.query_text_model(
            token,
            prompt,
            formatted_query,
            user_names=user_names,
            contextual_prompt=(
                "Respond in kind, as if you are present and involved. A user has mentioned you and needs your opinion "
                "on the conversation. Match the tone and style of preceding conversations, do not be overbearing and "
                "strive to blend in the conversation as closely as possible"
            ),
        )
        for page in response:
            await ctx.channel.send(page)

    async def get_openai_token(self):
        self.openai_settings = await self.bot.get_shared_api_tokens("openai")
        self.openai_token = self.openai_settings.get("key", None)
        return self.openai_token

    async def get_prefix(self, ctx: commands.Context) -> str:
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]
        return prefix

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
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
        if message.guild is None:
            await ctx.send("Chat command can only be used in an active thread! Please ask a question first.")
            return

        found_bot_response = False
        found_last_bot_response = False
        found_chat_input = False
        async for thread_message in channel.history(limit=100, oldest_first=False):
            try:
                if thread_message.author.bot:
                    await thread_message.delete()
                    found_bot_response = True
                elif found_bot_response:
                    found_last_bot_response = True

                if thread_message.clean_content.startswith(f"{prefix}chat"):
                    await thread_message.delete()
                    found_chat_input = True

                if found_chat_input and found_bot_response and found_last_bot_response:
                    break
            except Exception as e:
                break

        await message.delete()

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
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
            thread_name, formatted_query, user_names = await discord_handling.extract_chat_history_and_format(
                prefix, channel, message, author
            )
        except ValueError:
            await ctx.send("Something went wrong!")
            return

        tarot_guide = (self.data_dir / "tarot_guide.txt").read_text()
        lines_to_include = [(406, 799), (1444, 2904), (2906, 3299)]
        split_guide = tarot_guide.split("\n")
        passages = ["\n".join(split_guide[start : end + 1]) for start, end in lines_to_include]

        prompt = (
            "You are Wrin Sivinxi.\n"
            "Wrin is easily distracted, spacey, and ditzy with a focus on the present. She's very literal, and adopts "
            "an attitude of only valuing things in her life that add to it. If she likes you, you will know it, as "
            "she's very friendly and always cares deeply for friendships.\n"
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
        response = await model_querying.query_text_model(
            token, prompt, formatted_query, model="gpt-4o", user_names=user_names
        )
        await discord_handling.send_response(response, message, channel, thread_name)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
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

        # Check for mention cooldowns
        current_time = discord.utils.utcnow().timestamp()
        cooldown_duration = await self.config.guild(ctx.guild).cooldown()
        if author.id in self.mention_cooldowns:
            last_mentioned_time = self.mention_cooldowns[author.id]
            if current_time - last_mentioned_time < cooldown_duration:
                await ctx.send("You're on cooldown for mentioning the bot. Please wait a bit.")
                return

        if self.whois_dictionary is None:
            await self.reset_whois_dictionary()

        try:
            (thread_name, formatted_query, user_names) = await discord_handling.extract_chat_history_and_format(
                prefix, channel, message, author, whois_dict=self.whois_dictionary
            )
        except ValueError as e:
            await ctx.send(f"Error extracting chat history: {str(e)}")
            return

        token = await self.get_openai_token()
        prompt = await self.config.guild(ctx.guild).prompt()
        
        try:
            response = await model_querying.query_text_model(token, prompt, formatted_query, user_names=user_names)
            await discord_handling.send_response(response, message, channel, thread_name)
        except Exception as e:
            await ctx.send(f"Error processing the chat: {str(e)}")

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

    async def _image(self, channel: discord.abc.Messageable, message: discord, n_images=1, model: str = None):
        attachments: list[discord.Attachment] = [m for m in message.attachments if m.width]
        attachment = None
        if len(attachments) > 0:
            attachment: discord.Attachment = attachments[0]

        prompt_words = [w for i, w in enumerate(message.content.split(" ")) if i != 0]
        prompt: str = " ".join(prompt_words)
        thread_name = " ".join(prompt_words[:5]) + " image"
        token = await self.get_openai_token()
        try:
            response = await model_querying.query_image_model(token, prompt, attachment, n_images=n_images, model=model)
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
        attachments: list[discord.Attachment] = [m for m in message.attachments if m.width]
        if message.reference:
            referenced: discord.MessageReference = message.reference
            referenced_message: discord.Message = await channel.fetch_message(referenced.message_id)
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
            response = await model_querying.query_image_model(token, prompt, attachment, image_expansion=True)
        except ValueError:
            await ctx.send("Something went wrong!")
            return
        await discord_handling.send_response(response, message, channel, thread_name)