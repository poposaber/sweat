e = Exception("test")
print(str(e))

from common.game_version import GameVersion

v1 = GameVersion("1.0.0")
v2 = GameVersion("1.0.1")
v3 = GameVersion("1.1.0")
v4 = GameVersion("1.0.0")

print(f"v1: {v1}")
print(f"v2: {v2}")
print(f"v1 < v2: {v1 < v2}")
print(f"v2 > v1: {v2 > v1}")
print(f"v1 == v4: {v1 == v4}")
print(f"v3 > v2: {v3 > v2}")

try:
    GameVersion("invalid")
except ValueError as e:
    print(f"Caught expected error: {e}")

print("".isdigit())