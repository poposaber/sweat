from functools import total_ordering
from typing import Any

@total_ordering
class GameVersion:
    def __init__(self, version_str: str):
        try:
            parts = version_str.split('.')
            if len(parts) != 3:
                raise ValueError("Version string must be in format 'major.minor.patch'")
            self.major = int(parts[0])
            self.minor = int(parts[1])
            self.patch = int(parts[2])
        except ValueError as e:
            raise ValueError(f"Invalid version string '{version_str}': {e}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"GameVersion('{self}')"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GameVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, GameVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
