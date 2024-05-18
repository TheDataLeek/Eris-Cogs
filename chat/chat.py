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
            )
        }
        self.config.register_guild(**default_guild)
        self.data_dir = data_manager.bundled_data_path(self)
        self.whois_dictionary = None
        self.bot.add_listener(self.contextual_chat_handler, "on_message")

    @commands.command()
    @checks.mod()
    async def setprompt(self, ctx):
        """
        Set the real name of the user
        """
        message: discord.Message = ctx.message
        contents = " ".join(message.clean_content.split(" ")[1:])  # skip command
        await self.config.guild(ctx.guild).prompt.set(contents)

        await ctx.send("Done")

    @commands.command()
    async def showprompt(self, ctx):
        """
        Return the real name of the tagged user
        """
        prompt = await self.config.guild(ctx.guild).prompt()
        await ctx.send(prompt)

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
        response = await model_querying.query_text_model(
            token,
            prompt,
            formatted_query,
            user_names=user_names,
            contextual_prompt=(
                "What do you think about the following conversation? Respond in kind, as if you are present "
                "and involved. A user has tagged you and needs your opinion on the conversation."
            ),
        )
        for page in response:
            await channel.send(page)

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
        prefix = await self.get_prefix(ctx)

        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        if not isinstance(channel, discord.Thread):
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
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        prefix = await self.get_prefix(ctx)
        try:
            thread_name, formatted_query, _ = discord_handling.extract_chat_history_and_format(
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
            "You are to intepret the user-provided tarot reading below using the provided"
            f"reference guide. Please ask for clarification when needed, "
            "and allow for non-standard layouts to be described. Additionally if users provide images "
            "please read which cards are out, taking note of arrangement and orientation and provide the "
            "full reading in either case."
        )

        formatted_query = [
            *[{"role": "system", "content": passage} for passage in passages],
            *formatted_query,
        ]

        token = await self.get_openai_token()
        response = await model_querying.query_text_model(token, prompt, formatted_query, model="gpt-4o")
        await discord_handling.send_response(response, message, channel, thread_name)

    @commands.command()
    async def chat(self, ctx: commands.Context) -> None:
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        author: discord.Member = message.author
        prefix: str = await self.get_prefix(ctx)
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
        response = await model_querying.query_text_model(token, prompt, formatted_query, user_names=user_names)
        await discord_handling.send_response(response, message, channel, thread_name)

    @commands.command()
    async def image(self, ctx: commands.Context):
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
        await self._image(channel, message, model='dall-e-3')

    @commands.command()
    async def images(self, ctx: commands.Context):
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
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
        channel: discord.abc.Messageable = ctx.channel
        message: discord.Message = ctx.message
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
