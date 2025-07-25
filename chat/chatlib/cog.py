from .commands import ChatCommands
from .commands import Agent
from .commands import ImageCommands
from .commands import MetaCommands
from .commands import PathfinderCommands
from .commands import TarotCommands


class Chat(
    Agent,
    ChatCommands,
    ImageCommands,
    MetaCommands,
    PathfinderCommands,
    TarotCommands,
): ...
