# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of cogs (plugins) for [Red-DiscordBot](https://docs.discord.red/en/stable/), a self-hosted Discord bot framework. Each subdirectory is an independent cog that can be loaded into Red individually.

## Development commands

```bash
# Install dependencies (uv workspace with a nested `chat` package)
uv sync

# Lint
uv run ruff check .
uv run ruff format .

# Run tests
uv run pytest

# Regenerate README.md from each cog's info.json
uv run python generate_readme.py

# Run the bluesky_reposter CLI standalone
uv run python bluesky_reposter/bluesky_reposter.py <account>

# Run the chat CLI standalone
uv run chat/main.py
```

## Cog structure

Every cog follows this layout:

```
<cog_name>/
  __init__.py       # exports `async def setup(bot)` that registers the cog class
  <cog_name>.py     # cog implementation
  info.json         # metadata: name, short, description, ready (bool)
```

The `__init__.py` always ends with:

```python
async def setup(bot):
    cog = MyCog(bot)
    await bot.add_cog(cog)
```

Cog classes are declared as:

```python
BaseCog = getattr(commands, "Cog", object)

class MyCog(BaseCog):
    def __init__(self, bot_instance):
        ...
```

Red's `Config` is used for all persistent storage (`redbot.core.Config`). Each cog registers its own config with a unique `identifier` integer and `cog_name`.

## Event-driven cogs and ErisEventMixin

Cogs that respond to arbitrary messages (not commands) mix in `ErisEventMixin` from `eris_event_lib.py` at the repo root. Each cog directory that needs it has a symlink to the root file (Windows users must copy it manually).

`ErisEventMixin.allowed(ctx, message)` gates all passive message handlers — it checks:
- global + guild event toggles (managed by the `event_config` cog)
- channel whitelist/blacklist
- not a bot message, not a URL, not a command prefix
- dedup via `last_message_interacted_with_id`
- per-guild timeout

Cogs using this mixin register listeners in `__init__`:
```python
self.bot.add_listener(self.my_handler, "on_message")
```

and call `await self.allowed(ctx, message)` before acting, then `await self.log_last_message(ctx, message)` after.

## The `chat` cog (uv workspace member)

`chat/` is also a standalone uv package (`chat/pyproject.toml`) and the only workspace member. Its internals are organized as:

- `chatlib/cog.py` — `Chat` class assembled via multiple inheritance from mixins
- `chatlib/commands/base.py` — `ChatBase` with `Config` setup and OpenAI token retrieval
- `chatlib/commands/` — individual command groups (`ChatCommands`, `Agent`, `ImageCommands`, `MetaCommands`, `PathfinderCommands`, `TarotCommands`)
- `chatlib/utils/` — `model_querying.py`, `url_content.py`, `discord_handling.py`

The OpenAI API key is read from the `OPENAI_API_KEY` env var, falling back to Red's shared API tokens (`redbot.core.bot.get_shared_api_tokens("openai")`). Default model is `gpt-4o`.

## The `bluesky_reposter` cog

Uses APScheduler (`AsyncIOScheduler` with `MemoryJobStore`) to poll Bluesky every 2 minutes. The scheduler is a module-level singleton (`SCHEDULER`). Authentication credentials come from Red's shared API tokens (`bluesky` key) or `BSKY_USER`/`BSKY_PASS` env vars.

## Adding a new cog

1. Create `<cog_name>/` with `__init__.py`, `<cog_name>.py`, and `info.json`.
2. Set `"ready": true` in `info.json` when stable (controls README table).
3. If the cog listens to `on_message`, symlink `eris_event_lib.py` into the directory and mix in `ErisEventMixin`.
4. Run `uv run python generate_readme.py` to regenerate README.md.
