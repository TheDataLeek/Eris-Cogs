#!/usr/bin/env -S uv run

import inspect
import subprocess
import shlex

import typer
from rich import print

app = typer.Typer()


@app.command()
def main():
    from agentlib import Agent

    agent = Agent(None)
    print(agent)

    cmd = "redbot eris -v --token $CLIENT_TOKEN -p '>' --no-cogs --dev"
    print(cmd)
    subprocess.run(
        cmd,
        shell=True,
    )


if __name__ == "__main__":
    app()
