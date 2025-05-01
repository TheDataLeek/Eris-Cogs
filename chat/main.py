#!/usr/bin/env python3

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

    cmd = "redbot eris -v --token $CLIENT_TOKEN -p '>' --no-cogs --dev"
    print(cmd)
    subprocess.run(
        cmd,
        shell=True,
    )


if __name__ == "__main__":
    app()
