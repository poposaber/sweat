from dataclasses import dataclass

@dataclass
class GameCheckResultPayload: # this is sent by client
    game_name: str
    version: str
    sha256: str
