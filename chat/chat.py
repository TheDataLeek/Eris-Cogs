from __future__ import annotations

import discord
from redbot.core import commands, data_manager, bot, Config, checks
from redbot.core.bot import Red

from .chatlib import discord_handling, model_querying

BaseCog = getattr(commands, "Cog", object)


class Chat(BaseCog):
    def __init__(self, bot_instance: bot):
        self.bot: Red = bot_instance
        self.openai_settings = None
        self.openai_token = None
        self.config = Config.get_conf(
            self,
            identifier=23458972349810010102367456567347810101,
            force_registration=True,
            cog_name="chat",
        )
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
            "model": "gpt-4o",
        }
        self.config.register_guild(**default_guild)
        self.data_dir = data_manager.bundled_data_path(self)
        self.whois_dictionary = None
        self.bot.add_listener(self.contextual_chat_handler, "on_message")
        self.logged_messages = {}  # Initialize a dictionary to store messages per channel

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
            (_, formatted_query, user_names) = await discord_handling.extract_chat_history_and_format(
                prefix, channel, message, author, extract_full_history=True, whois_dict=self.whois_dictionary
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
            self.logged_messages[channel_id] = []  # Initialize the list for this channel

        if len(self.logged_messages[channel_id]) >= 20:  # Keep only the last 20 messages
            self.logged_messages[channel_id].pop(0)  # Remove the oldest message
        self.logged_messages[channel_id].append(message.content)  # Add the new message

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
            (thread_name, formatted_query, user_names) = await discord_handling.extract_chat_history_and_format(
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
        if channel_id not in self.logged_messages or not self.logged_messages[channel_id]:
            await ctx.send("No messages logged yet.")
            return

        # Send the logged messages for this specific channel
        for msg in self.logged_messages[channel_id]:
            await ctx.send(msg)

    @commands.command()
    async def generate_pf2e_character(self, ctx: commands.Context):
        """
        OK so the thinking here is that we can have her crawl through the site like a human would
        We'll start with the overview page, and then give her full crawling access over the entire site.
        We'll need to do this as a loop:
            * Starting page
            * What's my next step?
            * What links will I need?
            * download each link and cram into context window (leveraging the 1million token limit)
            * send a message each time we make an update

        Very similar to agent structure
        """
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        contents: str = " ".join(message.clean_content.split(" ")[1:])
        token = await self.get_openai_token()
        prefix: str = await self.get_prefix(ctx)
        model = await self.config.guild(ctx.guild).model()

        prompt = f"""
        You are to to generate a Pathfinder 2e character using provided reference materials in an automated agent 
        loop. Do not refer to Zoe or any other people in this process as you'll only be interacting with yourself and your own chain-of-thought.
        The process will be as follows.
        
            1. Using the provided reference materials, please generate a character concept by establishing their ancestry and class.
            2. Choose a name that fits their ancestry. Be creative with this name!
            3. Identify all urls needed to flesh out character details.
            
        In your response, insert all required URLS in the format, +[<url>].
        
        We'll then iterate on the following steps, and again, there's no human interactions here and you'll just be 
        responding to yourself, so keep your answers brief and to the point.
        
            1. Look through what answers you've already provided
            2. Download all urls and extract the relevant information
            3. Decide on the next steps
        
        We'll iterate until the character is fully fleshed out. If you have everything you need for the character,
        start your response with <<<DONE>>> followed by the character stat block.
        
        Your goal is to create a character that matches the priorities listed here: {contents}
        """

        classes = "https://2e.aonprd.com/Search.aspx?include-types=class&sort=name-asc&display=table&columns=icon_image+ability+hp+tradition+attack_proficiency+defense_proficiency+fortitude_proficiency+reflex_proficiency+will_proficiency+perception_proficiency+skill_proficiency+rarity+pfs"
        ancestries = "https://2e.aonprd.com/Search.aspx?include-types=ancestry&sort=rarity-asc+name-asc&display=table&columns=hp+size+speed+ability_boost+ability_flaw+language+vision+rarity+pfs"
        message.content += f"\n\n+[{classes}]\n\n+[{ancestries}]"

        thread = None
        for i in range(10):
            try:
                (thread_name, formatted_query, user_names) = await discord_handling.extract_chat_history_and_format(
                    prefix, channel, message, author
                )
            except ValueError:
                await ctx.send("Something went wrong!")
                return

            response = await model_querying.query_text_model(
                token, prompt, formatted_query, model=model, user_names=user_names
            )
            if i == 0:
                thread = await discord_handling.send_response(response, message, channel, thread_name)
            else:
                await discord_handling.send_response(response, message, thread, thread_name)
            if "<<<DONE>>>" in response:
                break
