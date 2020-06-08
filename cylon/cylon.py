#!/usr/bin/env python3.8

# stdlib
import sys
import os
import pathlib
import argparse
from time import sleep

# 3rd party
import aiohttp
import discord
from redbot.core import commands, bot
import keras

# local
from .eris_event_lib import ErisEventMixin


BaseCog = getattr(commands, "Cog", object)


def main():
    args = get_args()
    if args.train:
        pass
    elif args.deploy:
        pass
    else:
        raise NotImplemented('Model not trained')


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, default='data', help='Where to find input data')
    parser.add_argument('--train', action='store_true', default=False, help='Train Model')
    parser.add_argument('--deploy', action='store_true', default=False, help='Deploy to ec2')
    args = parser.parse_args()
    return args


class Cylon(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot: bot = bot_instance

        self.bot.add_listener(self.watch_message_history, "on_message")

    async def watch_message_history(self, message: discord.Message):
        pass

    @commands.command()
    async def tyler(self, ctx):
        async with ctx.typing():
            sleep(1)
            url = 'foobar'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    insult = await resp.text()


if __name__ == '__main__':
    sys.exit(main())
