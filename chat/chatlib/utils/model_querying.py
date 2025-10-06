from __future__ import annotations

import datetime as dt
import re
import asyncio
from PIL import Image
import base64
import io
from pprint import pformat
from typing import Dict, List

import discord
import openai
from redbot.core.utils import chat_formatting


async def query_text_model(
    token: str,
    prompt: str,
    formatted_query: str | list[dict],
    model: str = "gpt-4o",
    contextual_prompt: str = "",
    user_names=None,
    endpoint: str = "https://api.openai.com/v1/",
) -> list[str] | io.BytesIO:
    if user_names is None:
        user_names = {}
    formatted_usernames = pformat(user_names)

    today_string = dt.datetime.now().strftime(
        "The date is %A, %B %m, %Y. The time is %I:%M %p %Z"
    )

    system_prefix = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "text",
                    "text": (
                        "Users have names prefixed by an `@`, however we know the following real names and titles of "
                        f"some of the users involved,\n{formatted_usernames}\nPlease use their names when possible.\n"
                        "Your creator's handle is @erisaurus, and her name is Zoe.\n"
                        "To tag a user, use the format, `<@id>`, but only do this if you don't know their real name.\n"
                        f"{today_string}"
                    ),
                },
            ],
        },
    ]
    if contextual_prompt != "":
        system_prefix[0]["content"].append({"type": "text", "text": contextual_prompt})
    kwargs = {"model": model, "temperature": 1, "max_tokens": 2000}
    response = await construct_async_query(
        system_prefix + formatted_query,
        token,
        endpoint,
        **kwargs,
    )
    return response


async def generate_image(
    token: str,
    formatted_query: str | list[dict],
    attachment: discord.Attachment = None,
    image_expansion: bool = False,
    n_images: int = 1,
    model: str | None = None,
    endpoint: str = "https://api.openai.com/v1/",
) -> io.BytesIO:
    kwargs = {
        "n": n_images,
        "model": model or "dall-e-2",
        "response_format": "b64_json",
        "size": "1024x1024",
    }
    style = None
    if "vivid" in formatted_query:
        style = "vivid"
    elif "natural" in formatted_query:
        style = "natural"
    if (model is not None) and ("dall" in model):
        kwargs = {
            **{"model": "dall-e-3", "quality": "hd", "style": style},
            **kwargs,
        }
    else:
        kwargs = {
            "model": model,
            "n": 1,
            "size": "auto",
            "moderation": "low",
            "output_format": "png",
        }
    response = await construct_async_query(formatted_query, token, endpoint, **kwargs)

    return response


async def generate_image_edit(
    token: str,
    formatted_query: str | list[dict],
    attachment: discord.Attachment = None,
    endpoint: str = "https://api.openai.com/v1/",
):
    return await construct_async_query(
        formatted_query,
        token,
        endpoint=endpoint,
        model="gpt-image-1",
        image=await attachment.read(),
    )


async def construct_async_query(
    query: List[Dict],
    token: str,
    endpoint: str,
    **kwargs,
) -> list[str] | io.BytesIO:
    loop = asyncio.get_running_loop()
    time_to_sleep = 1
    exception_string = None
    while True:
        if time_to_sleep > 1:
            print(exception_string)
            raise TimeoutError(exception_string)
        try:
            response: str | io.BytesIO = await loop.run_in_executor(
                None,
                lambda: openai_client_and_query(token, query, endpoint, **kwargs),
            )
            break
        except Exception as e:
            exception_string = str(e)
            await asyncio.sleep(time_to_sleep**2)
            time_to_sleep += 1

    if isinstance(response, str):
        response = re.sub(r"\n{2,}", r"\n", response)  # strip multiple newlines
        return pagify_chat_result(response)

    return response


def openai_client_and_query(
    token: str,
    messages: str | list[dict],
    endpoint: str,
    **kwargs,
) -> str | io.BytesIO | list[io.BytesIO]:
    client: openai.OpenAI = openai.OpenAI(api_key=token, base_url=endpoint)
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if ("dall" in kwargs["model"]) or ("image" in kwargs["model"]):
        if "image" in kwargs:
            images = client.images.edit(prompt=messages, **kwargs)
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


async def generate_url_summary(
    url_name: str, url_markdown: str, model: openai.Client, token: str
) -> str:
    summary = "\n".join(
        await query_text_model(
            token,
            (
                "Your job is to summarize downloaded html web-pages that have been transformed to markdown. "
                "You will be used in an automated agent-pattern without human supervision, summarize the following in at most 3 sentences."
            ),
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"---\nFETCHED URL NAME: {url_name}\nCONTENTS:\n{url_markdown}\n---\n",
                        }
                    ],
                }
            ],
            model=model,
        )
    )
    return summary
