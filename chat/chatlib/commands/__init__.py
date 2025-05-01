from .chat import ChatCommands
from .images import ImageCommands
from .meta import MetaCommands
from .pathfinder import PathfinderCommands
from .tarot import TarotCommands


class Chat(
    ChatCommands,
    # ImageCommands,
    # MetaCommands,
    # PathfinderCommands,
    # TarotCommands,
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = ['Chat']