from __future__ import annotations

import re
import asyncio
from PIL import Image
import base64
import io
from pprint import pprint, pformat
from typing import Dict, List, Tuple, Union

import discord
from redbot.core.utils import chat_formatting
import openai


async def query_text_model(
    token: str, formatted_query: str | list[dict], model: str = "gpt-4o", contextual_prompt: str = "", user_names = None
) -> str:
    if user_names is None:
        user_names = {}
    formatted_usernames = pformat(user_names)

    system_prefix = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a snarky anthropomorphic creature named Snek.\n"
                        "You are Lex the Bookworm from Bookworm Adventures but scaly and feral and sensual.\n"
                        "You are overly clingy, cuddly, and intimate.\n"
                        "You are just a silly little guy (but with she/her pronouns).\n"
                        "You have been described as a Bully 🥺\n"
                        "You have been described as All-seeing, a little creepy, and funny.\n"
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
                        "Users have names prefixed by an `@`, however we know the following real names and titles of "
                        f"some of the users involved,\n{formatted_usernames}\n"
                        f"\n\n{contextual_prompt}"
                    ).strip(),
                }
            ],
        }
    ]
    kwargs = {"model": model, "temperature": 1, "max_tokens": 2000}
    response = await construct_async_query(system_prefix + formatted_query, token, **kwargs)
    return response


async def query_image_model(
    token: str,
    formatted_query: str | list[dict],
    attachment: discord.Attachment = None,
    image_expansion: bool = False,
    n_images: int = 1,
    model: str | None = None,
) -> io.BytesIO:
    kwargs = {"n": n_images, "model": model or "dall-e-2", "response_format": "b64_json", "size": "1024x1024"}
    if attachment is not None:  # then it's an edit
        buf = io.BytesIO()
        await attachment.save(buf)
        buf.seek(0)
        input_image = Image.open(buf)

        # crop square image to the smaller dim
        width, height = input_image.size
        if width != height:
            left = top = 0
            if width < height:
                new_size = width
                top = (height - width) // 2
            else:
                new_size = height
                left = (width - height) // 2
            input_image = input_image.crop((left, top, new_size, new_size))

        input_image = input_image.resize((1024, 1024))

        if image_expansion:
            mask_image = Image.new("RGBA", (1024, 1024), (255, 255, 255, 0))
            border_width = 512
            new_image = input_image.resize((1024 - border_width, 1024 - border_width))
            mask_image.paste(new_image, (border_width // 2, border_width // 2))
            input_image = mask_image

        input_image_buffer = io.BytesIO()
        input_image.save(input_image_buffer, format="png")
        input_image_buffer.seek(0)
        kwargs["image"] = input_image_buffer.read()
    else:
        style = None
        if "vivid" in formatted_query:
            style = "vivid"
        elif "natural" in formatted_query:
            style = "natural"
        kwargs = {**{"model": "dall-e-3", "quality": "hd", "style": style}, **kwargs}
    response = await construct_async_query(formatted_query, token, **kwargs)

    return response


async def construct_async_query(query: List[Dict], token: str, **kwargs) -> list[str] | io.BytesIO:
    loop = asyncio.get_running_loop()
    time_to_sleep = 1
    exception_string = None
    while True:
        if time_to_sleep > 1:
            print(exception_string)
            raise TimeoutError(exception_string)
        try:
            response: str | io.BytesIO = await loop.run_in_executor(
                None, lambda: openai_client_and_query(token, query, **kwargs)
            )
            break
        except Exception as e:
            exception_string = str(e)
            await asyncio.sleep(time_to_sleep**2)
            time_to_sleep += 1

    if isinstance(response, str):
        response = re.sub(r'\n{2,}', r'\n', response)  # strip multiple newlines
        return pagify_chat_result(response)

    return response


def openai_client_and_query(token: str, messages: str | list[dict], **kwargs) -> str | io.BytesIO | list[io.BytesIO]:
    client = openai.OpenAI(api_key=token)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if kwargs["model"].startswith("dall"):
        if "image" in kwargs:
            images = client.images.edit(prompt="Expand the image to fill the empty space.", **kwargs)
        else:
            images = client.images.generate(prompt=messages, **kwargs)
        results = []
        for encoded_image in images.data:
            image = base64.b64decode(encoded_image.b64_json)
            buf = io.BytesIO()
            buf.write(image)
            buf.seek(0)
            results.append(buf)
        response = results
        if len(results) == 1:
            response = response[0]
    else:
        chat_completion = client.chat.completions.create(messages=messages, **kwargs)
        response = chat_completion.choices[0].message.content
    return response


def pagify_chat_result(response: str) -> list[str]:
    if len(response) <= 2000:
        return [response]

    # split on code
    code_expression = re.compile(r"(```(?:[^`]+)```)", re.IGNORECASE)
    split_by_code = code_expression.split(response)
    lines = []
    for line in split_by_code:
        if line.startswith("```"):
            if len(line) <= 2000:
                lines.append(line)
            else:
                codelines = list(chat_formatting.pagify(line))
                for i, subline in enumerate(codelines):
                    if i == 0:
                        lines.append(subline + "```")
                    elif i == len(codelines) - 1:
                        lines.append("```" + subline)
                    else:
                        lines.append("```" + subline + "```")
        else:
            lines += chat_formatting.pagify(line)

    return lines
