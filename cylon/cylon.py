#!/usr/bin/env python3.8

# stdlib
import sys
import os
import pathlib
import argparse
from time import sleep
import json
from typing import List, Dict

# 3rd party
import aiohttp
import discord
from redbot.core import commands, bot, checks, data_manager
try:
    import keras
except ImportError:
    print('Warning! You wont be able to train the model')
    pass

# local
from .eris_event_lib import ErisEventMixin


BaseCog = getattr(commands, "Cog", object)


def main():
    args = get_args()
    if args.train:
        messages = load_from_json(args.data)
        processed = preprocess(messages)
    elif args.deploy:
        pass
    else:
        raise NotImplemented("Model not trained")


def load_from_json(datafile: pathlib.Path) -> List[Dict[str, str]]:
    """
   [
    {
        "author" : {
            "bot" : true,
            "discriminator" : "4886",
            "display_name" : "Headpat Harlot",
            "id" : 195663495189102593,
            "name" : "Snek"
        },
        "channel" : {
            "id" : 583118331444461568,
            "name" : "pineapple-day-v244"
        },
        "channel_mentions" : [],
        "content" : "490 messages saved from pineapple-day-v244",
        "id" : 651131471708422144,
        "mention_everyone" : false,
        "mentions" : [],
        "pinned" : false,
        "role_mentions" : [],
        "timestamp" : "2019-12-02 18:44:00",
        "tts" : false
    },
    """
    messages = [
        {
            'author': m['author']['id'],
            'content': m['content']
        }
        for m in
        json.loads(datafile.read_text())
    ]
    new_messages = []
    previous_author = None
    current_message = {}
    for m in messages:
        if m['author'] == previous_author:
            current_message['content'] += f"\n{m['content']}"
        else:
            if current_message:
                new_messages.append(current_message)
            current_message = m
            previous_author = m['author']
    new_messages.append(current_message)
    return new_messages


def preprocess(text: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # https://keras.io/api/preprocessing/text/
    tokenizer = keras.preprocessing.text.Tokenizer(
        num_words=None,  # keep all words
        filters='"#$%&()*+-<=>@[\\]^_`{|}~\t0123456789',  # edited from docs to include what we care about and exclude nums
        lower=False,    # don't convert to lowercase
        split=" ",  # default
    )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data", type=str, default=None, help="Where to find input data"
    )
    parser.add_argument(
        "--train", action="store_true", default=False, help="Train Model"
    )
    parser.add_argument(
        "--deploy", action="store_true", default=False, help="Deploy to ec2"
    )
    args = parser.parse_args()
    if args.data is None:
        raise FileNotFoundError('Please provide a data file!')
    return args


class Cylon(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot: bot = bot_instance
        self.data_dir = data_manager.bundled_data_path(self)

        self.bot.add_listener(self.watch_message_history, "on_message")

    @commands.command()
    @checks.is_owner()
    async def reap(self, ctx):
        channel: discord.TextChannel = ctx.channel
        server: discord.Guild = ctx.guild

        message_list = []

        # let's start with just the latest 500
        message: discord.Message
        last_message_examined: discord.Message = None
        message_count = 0
        while True:
            chunk = await channel.history(
                limit=500, before=last_message_examined
            ).flatten()
            if len(chunk) == 0:
                break
            message_count += len(chunk)
            for message in chunk:
                if message.clean_content.startswith('.'):
                    continue
                if message.author.bot:
                    continue
                message_list.append({
                    'author': message.author.id,
                    'content': message.clean_content,
                })

            last_message_examined = message

        message_list = list(set(message_list))
        filename = f"{server.name}-{channel.name}.json"
        output_file = self.data_dir / filename
        output_file.write_text(json.dumps(message_list))

        await ctx.send(
            f"Done. Processed {message_count} messages."
        )

    async def watch_message_history(self, message: discord.Message):
        pass

    @commands.command()
    async def cylon(self, ctx):
        return
        async with ctx.typing():
            sleep(1)
            url = "foobar"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    insult = await resp.text()


if __name__ == "__main__":
    sys.exit(main())
