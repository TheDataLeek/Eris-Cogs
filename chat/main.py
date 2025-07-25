#!/usr/bin/env -S uv run

import inspect
import subprocess
import shlex

import typer
from rich import print

app = typer.Typer()


@app.command()
def main():
    from chatlib import Chat

    chat = Chat(None)
    print(chat)


if __name__ == "__main__":
    app()
