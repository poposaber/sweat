import customtkinter
from typing import Callable, Optional
from .block_container import BlockContainer
from .game_block import GameBlock

class GameBlockContainer(BlockContainer):
    def __init__(self, master, width: int = 400, height: int = 300, columns: int = 5):
        super().__init__(master, width=width, height=height, columns=columns)
        self.block_dict: dict[str, GameBlock] = {}

    def add_block(self, game_name: str, version: str, min_players: int, max_players: int, game_cover: Optional[bytes] = None, command: Optional[Callable[[], None]] = None):
        block = super().add_block(GameBlock, game_name, version, min_players, max_players, game_cover, command)
        self.block_dict[game_name] = block
    
    def get_block(self, game_name: str) -> Optional[GameBlock]:
        return self.block_dict.get(game_name)

    def add_blocks(self, games: list[tuple[str, str, int, int, Optional[bytes], Optional[Callable[[], None]]]]):
        for game in games:
            self.add_block(*game)

    def set_blocks(self, games: list[tuple[str, str, int, int, Optional[bytes], Optional[Callable[[], None]]]]):
        self.clear_blocks()
        self.block_dict.clear()
        self.add_blocks(games)