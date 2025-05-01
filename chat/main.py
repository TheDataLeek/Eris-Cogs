#!/usr/bin/env python3

import typer

app = typer.Typer()


@app.command()
def main():
    from chatlib import Chat
    chat = Chat(None)
    print(chat)


if __name__ == '__main__':
    app()