from .. import discord_handling, model_querying, content

from .base import ChatBase

from .chat import ChatCommands
from .images import ImageCommands
from .meta import MetaCommands
from .pathfinder import PathfinderCommands
from .tarot import TarotCommands


class Chat(
    ChatBase,
    ChatCommands,
    ImageCommands,
    MetaCommands,
    PathfinderCommands,
    TarotCommands,
): ...
