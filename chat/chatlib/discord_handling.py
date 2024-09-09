from __future__ import annotations

import re
import datetime as dt
import json
import io
from typing import Dict, List, Tuple, Union
import string
import aiohttp

from markdownify import markdownify as md

import discord
from redbot.core import commands  # Add this import

async def has_role_check(ctx: commands.Context) -> bool:
    """Check if the user has the required role to use commands."""
    role_id = await ctx.cog.config.guild(ctx.guild).role_name()
    if role_id is None:
        return True  # No role set, allow all
    role = ctx.guild.get_role(role_id)
    return role in ctx.author.roles if role else False

async def extract_chat_history_and_format(
    ctx: commands.Context,  # Add ctx as a parameter
    prefix: None | str,
    channel: discord.abc.Messageable,
    message: discord.Message,
    author: discord.Member,
    extract_full_history: bool = False,
    whois_dict: dict = None,
) -> tuple[str, list[dict], dict[str, dict[str, str]]]:
    if whois_dict is None:
        whois_dict = {}
    guild: discord.Guild = message.guild
    thread_name = "foo"
    formatted_query = []
    query = message.clean_content.split(" ")[1:]
    skip_command_word = f"{prefix}chat"

    how_far_back = dt.timedelta(minutes=30)
    after = dt.datetime.now() - how_far_back

    if not query:
        raise ValueError("Query not supplied!")

    users_involved = []
    if isinstance(channel, discord.TextChannel):
        formatted_query = " ".join(query)
        thread_name = (" ".join(formatted_query.split(" ")[:5]))[:80] + "..."

        # Check if the user has the required role
        if not await has_role_check(ctx):  # Now ctx is defined
            raise ValueError("You do not have permission to use this command.")

        if extract_full_history:
            formatted_query, users_involved = await extract_history(
                channel, author, skip_command_word=None, after=after
            )
        else:
            extracted_message, pages = await extract_message(formatted_query, False, skip_command_word)
            formatted_query = [
                {
                    "role": "user",
                    "name": clean_username(author.name),
                    "content": [
                        {"type": "text", "text": extracted_message},
                        *[await format_attachment(attachment) for attachment in message.attachments],
                    ],
                }
            ] + pages
            users_involved = [author] + message.mentions
    elif isinstance(channel, discord.Thread):
        if extract_full_history:
            formatted_query, users_involved = await extract_history(
                channel, author, skip_command_word=None, after=after
            )
        else:
            formatted_query, users_involved = await extract_history(
                channel, author, skip_command_word=skip_command_word
            )

    users_involved = list(set(users_involved))  # remove duplicates
    users = {
        str(user.id): {
            "username": user.name,
            "author": clean_username(user.name),
            "nickname": user.nick  if isinstance(user, discord.Member) else user.name,
            "real name": find_user(guild.name, user, whois_dict),
        }
        for user in users_involved
    }
    return thread_name, formatted_query, users


async def extract_history(
    channel_or_thread: discord.abc.Messageable,
    author: discord.Member,
    skip_command_word: str = None,
    limit: int = 100,
    after=None,
):
    keep_all_words = skip_command_word is None
    history = []
    users_involved = []
    async for thread_message in channel_or_thread.history(limit=limit, oldest_first=False, after=after):
        if thread_message.author.bot or keep_all_words or thread_message.clean_content.startswith(skip_command_word):
            cleaned_message, pages = await extract_message(
                thread_message.clean_content, keep_all_words, skip_command_word
            )
            history += pages
            history.append(
                {
                    "role": "assistant" if thread_message.author.bot else "user",
                    "name": clean_username(thread_message.author.name),
                    "content": [
                        {"type": "text", "text": cleaned_message},
                        *[{"type": "text", "text": json.dumps(embed.to_dict())} for embed in thread_message.embeds],
                        *[await format_attachment(attachment) for attachment in thread_message.attachments],
                    ],
                }
            )
            users_involved.append(thread_message.author)
            users_involved += thread_message.mentions

    if isinstance(channel_or_thread, discord.Thread):
        starter_message = channel_or_thread.starter_message
        if starter_message is not None:
            cleaned_message, pages = await extract_message(
                starter_message.clean_content, keep_all_words, skip_command_word
            )
            history += pages
            history.append(
                {
                    "role": "user",
                    "name": clean_username(author.name),
                    "content": [
                        {"type": "text", "text": cleaned_message},
                        *[await format_attachment(attachment) for attachment in starter_message.attachments],
                    ],
                }
            )
            users_involved.append(author)
            users_involved += starter_message.mentions

    history = history[::-1]  # flip to oldest first
    return history, users_involved


async def fetch_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return ""
            page_content = await resp.text()
            markdown_content = md(page_content)
    return markdown_content


async def extract_message(message, keep_all_words, skip_command_word):
    words = message.split(" ")
    keep_words = []
    page_contents = []
    for word in words:
        match = re.match(r"\+\[(https?://.+?)\]", word, flags=re.IGNORECASE)
        if match:
            url = match.group(1)
            page_contents.append((url, await fetch_url(url)))
        elif keep_all_words or (not word.startswith(skip_command_word)):
            keep_words.append(word)

    cleaned_message = " ".join(keep_words)

    pages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": f"---\n{url}---\n{page}\n---\n"} for url, page in page_contents],
        }
    ]

    return cleaned_message, pages


async def send_response(
    ctx: commands.Context,  # Add ctx as a parameter
    response: str | io.BytesIO | list[io.BytesIO],
    message: discord.Message,
    channel_or_thread: discord.abc.Messageable,
    thread_name: str,
):
    if isinstance(channel_or_thread, discord.TextChannel):
        channel_or_thread: discord.Thread = await message.create_thread(name=thread_name)

    # Check if the role check is enabled before enforcing it
    if ctx.cog.role_check_enabled and not await has_role_check(ctx):
        await channel_or_thread.send("You do not have permission to mention the bot.")
        return

    if isinstance(response, list):
        if isinstance(response[0], io.BytesIO):  # then we have multiple images
            await channel_or_thread.send(
                files=[discord.File(buf, filename=f"{i}.png") for i, buf in enumerate(response)]
            )
        else:
            for page in response:
                await channel_or_thread.send(page)
    else:
        filename = thread_name.replace(" ", "_") + ".png"
        await channel_or_thread.send(file=discord.File(response, filename=filename))


def extract_system_messages_from_message(message: str) -> Tuple[str, List[str]]:
    # extract the system messages
    # https://regex101.com/r/5VTsQ7/1
    system_message_expression = re.compile(r"(`+)([^`]+)\1", re.IGNORECASE)

    system_messages = [msg for tick, msg in system_message_expression.findall(message)]

    # now remove them
    message_without_system, _ = system_message_expression.subn("", message)
    query = message_without_system.strip()

    return query, system_messages


async def format_attachment(attachment: discord.Attachment) -> dict:
    mimetype: str = (attachment.content_type or "").lower()
    filename: str = attachment.filename.lower()
    formatted_attachment = {"type": "text", "text": "<MISSING ATTACHMENT>"}
    permitted_extensions = [
        "txt",
        "text",
        "json",
        "py",
        "md",
        "c",
        "h",
        "cpp",
        "hpp",
        "java",
        "js",
        "ts",
        "tsx",
        "html",
        "css",
        "scss",
        "xml",
    ]
    has_valid_extension = any([filename.endswith(ext) for ext in permitted_extensions])
    text = None
    if has_valid_extension or "text" in mimetype:  # if it's text
        buf = io.BytesIO()
        await attachment.save(buf)
        buf.seek(0)
        text = buf.read().decode("utf-8")
        formatted_attachment = {"type": "text", "text": text}
    elif attachment.width and "image" in attachment.content_type:
        formatted_attachment = {"type": "image_url", "image_url": {"url": attachment.url}}
    if text is None:
        print(formatted_attachment)
    else:
        print(text[:25] + "..." + text[-25:])
    # otherwise it's not supported
    return formatted_attachment


def clean_username(name: str) -> str:
    name = name.lower()
    name = "".join(c for c in name if c in string.ascii_lowercase)
    return name


def find_user(guild_name: str, user: discord.Member, whois_dict) -> str:
    if guild_name in whois_dict:
        userid = str(user.id)
        if userid in whois_dict[guild_name]:
            return whois_dict[guild_name][userid]