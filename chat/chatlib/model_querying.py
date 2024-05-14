from __future__ import annotations

import asyncio
from PIL import Image
import base64
import io
from pprint import pprint
from typing import Dict, List, Tuple, Union

import discord
import openai

from .discord_handling import pagify_chat_result


async def query_text_model(
    token: str,
    formatted_query: str | list[dict],
    model: str = "gpt-4-vision-preview",
    contextual_prompt: str = "",
) -> str:
    system_prefix = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a helpful robot user named Snek. "
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
                        "otherwise requested."
                        f"\n\n{contextual_prompt}"
                    ).strip(),
                }
            ],
        }
    ]
    kwargs = {
        "model": model,
        "temperature": 1,
        "max_tokens": 2000,
    }
    response = await construct_async_query(system_prefix + formatted_query, token, **kwargs)
    return response


async def query_image_model(
    token: str,
    formatted_query: str | list[dict],
    attachment: discord.Attachment = None,
    image_expansion: bool = False,
) -> io.BytesIO:
    kwargs = {
        "n": 1,
        "model": "dall-e-2",
        "response_format": "b64_json",
        "size": "1024x1024",
    }
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
        kwargs = {
            **kwargs,
            **{
                "model": "dall-e-3",
                "quality": "hd",
                "style": style,
            },
        }
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
        return pagify_chat_result(response)

    return response


def openai_client_and_query(token: str, messages: str | list[dict], **kwargs) -> str | io.BytesIO:
    client = openai.OpenAI(api_key=token)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if kwargs["model"].startswith("dall"):
        if "image" in kwargs:
            images = client.images.edit(prompt="Expand the image to fill the empty space.", **kwargs)
        else:
            images = client.images.generate(prompt=messages, **kwargs)
        encoded_image = images.data[0].b64_json
        image = base64.b64decode(encoded_image)
        buf = io.BytesIO()
        buf.write(image)
        buf.seek(0)
        response = buf
    else:
        chat_completion = client.chat.completions.create(
            messages=messages,
            **kwargs,
        )
        response = chat_completion.choices[0].message.content
    return response
