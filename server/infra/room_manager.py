import logging
import threading
import random
import string
from dataclasses import dataclass, field
from .errors import *
from protocol.enums import RoomStatus
from typing import Optional, Callable

ROOM_ID_GENERATION_MAX_ATTEMPTS = 36 ** 5 # 60,466,176
ROOM_ID_LENGTH = 5

logger = logging.getLogger(__name__)

@dataclass
class Room:
    host: str
    game_name: str
    player_list: list[str]
    max_players: int
    status: RoomStatus = RoomStatus.WAITING
    ready_player_set: set[str] = field(default_factory=set)

class RoomManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}
        self._player_room_map: dict[str, str] = {}
        self._free_ids: list[str] = [] # Cache of pre-validated IDs
        self._room_player_lock = threading.Lock()
        self._id_pool_lock = threading.Lock()
        self._fill_id_pool()

    def _fill_id_pool(self, batch_size=100):
        chars = string.digits + string.ascii_lowercase
        new_ids = []
        attempts = 0
        
        # 1. Generate candidates locally (no lock needed)
        while len(new_ids) < batch_size and attempts < batch_size * 4:
            room_id = ''.join(random.choices(chars, k=ROOM_ID_LENGTH))
            # Optimization: mild race condition on _rooms check is acceptable 
            # because create_room will fail if ID exists, or we catch it at append time
            if room_id not in self._rooms and room_id not in new_ids:
                new_ids.append(room_id)
            attempts += 1

        # 2. Bulk add to shared pool (lock held once)
        with self._id_pool_lock:
            for rid in new_ids:
                if rid not in self._free_ids and rid not in self._rooms:
                    self._free_ids.append(rid)

    def _generate_room_id(self) -> str:
        # Optimistic check first
        with self._id_pool_lock:
            if self._free_ids:
                return self._free_ids.pop()

        # If empty, fill logic
        self._fill_id_pool()

        # Try pop again
        with self._id_pool_lock:
            if self._free_ids:
                return self._free_ids.pop()

        # If still empty (extremely full server), fall back to direct generation
        chars = string.digits + string.ascii_lowercase
        attempts = 0
        while attempts < ROOM_ID_GENERATION_MAX_ATTEMPTS:
            room_id = ''.join(random.choices(chars, k=ROOM_ID_LENGTH))
            if room_id not in self._rooms:
                return room_id
            attempts += 1
        raise RoomIDGenerationError("Failed to generate unique room ID after maximum attempts")

    def create_room(self, host_username: str, game_name: str, max_players: int) -> str:
        if host_username in self._player_room_map:
            logger.warning(f"Create room failed: user {host_username} is already in a room")
            raise PlayerAlreadyInRoomError(f"User {host_username} is already in a room")
        room_id = self._generate_room_id()
        with self._room_player_lock:
            self._rooms[room_id] = Room(
                host=host_username, game_name=game_name, player_list=[host_username], max_players=max_players)
            self._player_room_map[host_username] = room_id
        logger.info(f"Room created: room_id={room_id}, host={host_username}, game={game_name}")
        return room_id
    
    def add_player_to_room(self, room_id: str, username: str) -> None:
        with self._room_player_lock:
            room = self._rooms.get(room_id)
            if not room:
                logger.warning(f"Add player to room failed: room_id={room_id} not found")
                raise RoomNotFoundError(f"Room {room_id} not found")
            if len(room.player_list) >= room.max_players:
                logger.warning(f"Add player to room failed: room_id={room_id} is full")
                raise RoomFullError(f"Room {room_id} is full")
            if username in room.player_list:
                logger.warning(f"Add player to room failed: user {username} already in room {room_id}")
                raise PlayerAlreadyInRoomError(f"User {username} is already in room {room_id}")
            if username in self._player_room_map:
                logger.warning(f"Add player to room failed: user {username} is already in another room")
                raise PlayerAlreadyInRoomError(f"User {username} is already in another room {self._player_room_map[username]}")
            if room.status != RoomStatus.WAITING:
                logger.warning(f"Add player to room failed: room_id={room_id} is not in WAITING status")
                raise RoomClosedError(f"Room {room_id} is not open for joining")
            room.player_list.append(username)
            self._player_room_map[username] = room_id
            logger.info(f"User {username} added to room {room_id}")


    def remove_player_from_room(self, room_id: str, username: str, on_delete_room_callback: Optional[Callable[[str], None]] = None) -> None:
        with self._room_player_lock:
            room = self._rooms.get(room_id)
            if not room:
                logger.warning(f"Leave room failed: room_id={room_id} not found")
                raise RoomNotFoundError(f"Room {room_id} not found")
            if username in room.player_list:
                room.player_list.remove(username)
                room.ready_player_set.discard(username)
                logger.info(f"User {username} left room {room_id}")
                if not room.player_list:
                    del self._rooms[room_id]
                    logger.info(f"Room {room_id} deleted as it became empty")
                    if on_delete_room_callback:
                        on_delete_room_callback(room_id)
                elif username == room.host:
                    room.host = room.player_list[0]
                    logger.info(f"Host of room {room_id} changed to {room.host}")
                self._player_room_map.pop(username, None)
            else:
                logger.warning(f"Leave room failed: user {username} not in room {room_id}")
                raise PlayerNotInRoomError(f"User {username} is not in room {room_id}")
            
    def set_room_status(self, room_id: str, status: RoomStatus) -> None:
        with self._room_player_lock:
            room = self._rooms.get(room_id)
            if not room:
                logger.warning(f"Set room status failed: room_id={room_id} not found")
                raise RoomNotFoundError(f"Room {room_id} not found")
            room.status = status
            logger.info(f"Room {room_id} status set to {status.name}")

    def clear_room_player_ready(self, room_id: str) -> None:
        with self._room_player_lock:
            room = self._rooms.get(room_id)
            if not room:
                logger.warning(f"Clear ready status failed: room_id={room_id} not found")
                raise RoomNotFoundError(f"Room {room_id} not found")
            room.ready_player_set.clear()
            logger.info(f"Cleared ready status for all players in room {room_id}")

    def add_room_player_ready(self, room_id: str, username: str) -> None:
        with self._room_player_lock:
            room = self._rooms.get(room_id)
            if not room:
                logger.warning(f"Set player ready failed: room_id={room_id} not found")
                raise RoomNotFoundError(f"Room {room_id} not found")
            if username not in room.player_list:
                logger.warning(f"Set player ready failed: user {username} not in room {room_id}")
                raise PlayerNotInRoomError(f"User {username} is not in room {room_id}")
            room.ready_player_set.add(username)
            logger.info(f"User {username} set as ready in room {room_id}")

    def is_player_all_ready(self, room_id: str) -> bool:
        with self._room_player_lock:
            room = self._rooms.get(room_id)
            if not room:
                logger.warning(f"Check all ready failed: room_id={room_id} not found")
                raise RoomNotFoundError(f"Room {room_id} not found")
            return len(room.ready_player_set) == len(room.player_list)
            
    def get_all_rooms(self) -> dict[str, Room]:
        with self._room_player_lock:
            return self._rooms.copy()
        
    def get_room_by_player(self, username: str) -> Room | None:
        with self._room_player_lock:
            room_id = self._player_room_map.get(username)
            if room_id:
                return self._rooms.get(room_id)
            return None
        
    def get_room_id_by_player(self, username: str) -> str | None:
        with self._room_player_lock:
            return self._player_room_map.get(username)
        
    def get_room_by_room_id(self, room_id: str) -> Room | None:
        with self._room_player_lock:
            return self._rooms.get(room_id)
        
    def output_status(self):
        with self._room_player_lock:
            if not self._rooms:
                logger.info("No active rooms.")
            for room_id, room in self._rooms.items():
                logger.info(f"Room ID: {room_id}, Host: {room.host}, Game: {room.game_name}, Players: {room.player_list}")
        with self._id_pool_lock:
            logger.debug(f"Free Room ID Pool: {self._free_ids}")
        
        