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


async def extract_chat_history_and_format(
    prefix: None | str,
    channel: discord.abc.Messageable,
    message: discord.Message,
    author: discord.Member,
    extract_full_history: bool = False,
) -> tuple[str, list[dict]]:
    thread_name = "foo"
    formatted_query = []
    query = message.clean_content.split(" ")[1:]
    skip_command_word = f"{prefix}chat"

    how_far_back = dt.timedelta(minutes=30)
    after = dt.datetime.now() - how_far_back

    if not query:
        raise ValueError("Query not supplied!")

    if isinstance(channel, discord.TextChannel):
        formatted_query = " ".join(query)
        thread_name = (" ".join(formatted_query.split(" ")[:5]))[:80] + "..."

        if extract_full_history:
            formatted_query = await extract_history(channel, author, skip_command_word=None, after=after)
        else:
            extracted_message, page_contents = await extract_message(formatted_query, False, skip_command_word)
            formatted_query = [
                {
                    "role": "user",
                    "name": clean_username(author.name),
                    "content": [
                        {"type": "text", "text": extracted_message},
                        *[await format_attachment(attachment) for attachment in message.attachments],
                    ],
                }
            ] + [
                {"role": "user", "name": clean_username(author.name), "content": {"type": "text", "text": page}}
                for url, page in page_contents
            ]
    elif isinstance(channel, discord.Thread):
        if extract_full_history:
            formatted_query = await extract_history(channel, author, skip_command_word=None, after=after)
        else:
            formatted_query = await extract_history(channel, author, skip_command_word=skip_command_word)

    return thread_name, formatted_query


async def extract_history(
    channel_or_thread: discord.abc.Messageable,
    author: discord.Member,
    skip_command_word: str = None,
    limit: int = 100,
    after=None,
):
    keep_all_words = skip_command_word is None
    history = []
    async for thread_message in channel_or_thread.history(limit=limit, oldest_first=False, after=after):
        if thread_message.author.bot or keep_all_words or thread_message.clean_content.startswith(skip_command_word):
            cleaned_message, page_contents = await extract_message(
                thread_message.content, keep_all_words, skip_command_word
            )
            for url, page in page_contents:
                history.append(
                    {"role": "user", "name": clean_username(author.name), "content": {"type": "text", "text": page}}
                )
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

    if isinstance(channel_or_thread, discord.Thread):
        starter_message = channel_or_thread.starter_message
        if starter_message is not None:
            cleaned_message, page_contents = await extract_message(
                starter_message.content, keep_all_words, skip_command_word
            )
            for url, page in page_contents:
                history.append(
                    {"role": "user", "name": clean_username(author.name), "content": {"type": "text", "text": page}}
                )
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

    history = history[::-1]  # flip to oldest first
    return history


async def fetch_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
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

    return cleaned_message, page_contents


async def send_response(
    response: str | io.BytesIO, message: discord.Message, channel_or_thread: discord.abc.Messageable, thread_name: str
):
    if isinstance(channel_or_thread, discord.TextChannel):
        channel_or_thread: discord.Thread = await message.create_thread(name=thread_name)

    if isinstance(response, list):
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
    mimetype: str = attachment.content_type.lower()
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
    elif attachment.width:  # then it's an image less than 20MB
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
