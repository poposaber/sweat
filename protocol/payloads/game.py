from dataclasses import dataclass

@dataclass
class UploadGameInitPayload:
    name: str
    version: str
    min_players: int
    max_players: int
    sha256: str
    total_size: int

@dataclass
class UploadGameChunkPayload:
    upload_id: str
    chunk_index: int
    data: bytes

@dataclass
class UploadGameFinishPayload:
    upload_id: str

@dataclass
class UploadGameInitResponsePayload:
    upload_id: str
    chunk_size: int

@dataclass
class FetchMyWorksResponsePayload:
    works: list[tuple[str, str, int, int]] # (game_name, version, min_players, max_players)

@dataclass
class FetchStorePayload:
    page: int
    page_size: int

@dataclass
class FetchStoreResponsePayload:
    games: list[tuple[str, str, int, int]] # (game_name, version, min_players, max_players)
    total_count: int

@dataclass
class FetchGameCoverPayload:
    game_name: str

@dataclass
class FetchGameCoverResponsePayload:
    game_name: str
    cover_data: bytes
