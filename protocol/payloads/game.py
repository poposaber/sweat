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
