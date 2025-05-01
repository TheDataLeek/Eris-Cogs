from .commands import ChatCommands
from .commands import ImageCommands
from .commands import MetaCommands
from .commands import PathfinderCommands
from .commands import TarotCommands


class Chat(
    ChatCommands,
    ImageCommands,
    MetaCommands,
    PathfinderCommands,
    TarotCommands,
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

