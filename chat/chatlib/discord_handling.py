from __future__ import annotations

import re
import json
import io
from typing import Dict, List, Tuple, Union
import string

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

    if not query:
        raise ValueError("Query not supplied!")

    if isinstance(channel, discord.TextChannel):
        formatted_query = " ".join(query)

        thread_name = " ".join(formatted_query.split(" ")[:5]) + "..."
        if extract_full_history:
            formatted_query = extract_history(channel, author, skip_command_word=None)
        else:
            formatted_query = [
                {
                    "role": "user",
                    "name": clean_username(author.name),
                    "content": [
                        {"type": "text", "text": formatted_query},
                        *[await format_attachment(attachment) for attachment in message.attachments],
                    ],
                }
            ]
    elif isinstance(channel, discord.Thread):
        if extract_full_history:
            skip_command_word = None
        formatted_query = extract_history(channel, author, skip_command_word=skip_command_word)

    return thread_name, formatted_query


async def extract_history(
    channel_or_thread: discord.abc.Messageable, author: discord.Member, skip_command_word: str = None, limit: int = 100
):
    keep_all_words = skip_command_word is None
    history = [
        {
            "role": "assistant" if thread_message.author.bot else "user",
            "name": clean_username(thread_message.author.name),
            "content": [
                {
                    "type": "text",
                    "text": " ".join(
                        w
                        for w in thread_message.clean_content.split(" ")
                        if keep_all_words or (not w.startswith(skip_command_word))
                    ),
                },
                *[{"type": "text", "text": json.dumps(embed.to_dict())} for embed in thread_message.embeds],
                *[await format_attachment(attachment) for attachment in thread_message.attachments],
            ],
        }
        async for thread_message in channel_or_thread.history(limit=limit, oldest_first=False)
        if thread_message.author.bot or keep_all_words or thread_message.clean_content.startswith(skip_command_word)
    ]

    if isinstance(channel_or_thread, discord.Thread):
        starter_message = channel_or_thread.starter_message
        if starter_message is not None:
            message_without_command = " ".join(starter_message.content.split(" ")[1:])
            history.append(
                {
                    "role": "user",
                    "name": clean_username(author.name),
                    "content": [
                        {"type": "text", "text": message_without_command},
                        *[await format_attachment(attachment) for attachment in starter_message.attachments],
                    ],
                }
            )

    history = history[::-1]  # flip to oldest first
    return history


async def send_response(
    response: str | io.BytesIO,
    message: discord.Message,
    channel_or_thread: discord.abc.Messageable,
    thread_name: str,
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
    elif attachment.width:  # then it's an image
        formatted_attachment = {
            "type": "image_url",
            "image_url": {"url": attachment.url},
        }
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
