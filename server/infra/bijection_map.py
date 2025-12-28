import threading
from typing import Generic, TypeVar

K1 = TypeVar('K1')
K2 = TypeVar('K2')

class BijectionMap(Generic[K1, K2]):
    """A thread-safe bijection map between two sets of items."""
    def __init__(self):
        self._forward: dict[K1, K2] = {}
        self._backward: dict[K2, K1] = {}
        self._lock = threading.Lock()

    def add(self, key1: K1, key2: K2):
        with self._lock:
            if key1 in self._forward or key2 in self._backward:
                raise KeyError("One of the keys is already present in the bijection map")
            self._forward[key1] = key2
            self._backward[key2] = key1

    def remove_by_key1(self, key1: K1):
        with self._lock:
            if key1 not in self._forward:
                raise KeyError("Key1 not found in the bijection map")
            key2 = self._forward.pop(key1)
            del self._backward[key2]

    def remove_by_key2(self, key2: K2):
        with self._lock:
            if key2 not in self._backward:
                raise KeyError("Key2 not found in the bijection map")
            key1 = self._backward.pop(key2)
            del self._forward[key1]

    def get_by_key1(self, key1: K1) -> K2 | None:
        with self._lock:
            return self._forward.get(key1)

    def get_by_key2(self, key2: K2) -> K1 | None:
        with self._lock:
            return self._backward.get(key2)

    def clear(self):
        with self._lock:
            self._forward.clear()
            self._backward.clear()

    def get_all_key1s(self) -> list[K1]:
        with self._lock:
            return list(self._forward.keys())
        
    def get_all_key2s(self) -> list[K2]:
        with self._lock:
            return list(self._backward.keys())