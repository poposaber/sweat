from dataclasses import dataclass

@dataclass
class Credential:
    username: str
    password: str
    role: str