import logging
import os
from protocol.payloads.common import EmptyPayload

from protocol.payloads.game_launch import GameCheckResultPayload

from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.room_manager import RoomManager
from server.infra.game_process_manager import GameProcessManager
from session.session import Session
from protocol.payloads.events import RoomUpdatedEventPayload, MyRoomUpdatedEventPayload, GameCheckEventPayload, GameStartResultEventPayload
from protocol.enums import Role, Action, RoomStatus
from protocol.message import Message
import server.infra.broadcaster as broadcaster

logger = logging.getLogger(__name__)

def handle_start_game(room_manager: RoomManager, game_process_manager: GameProcessManager, db: Database, session_user_map: SessionUserMap, session: Session) -> tuple[EmptyPayload, bool, str]:
    user_info = session_user_map.get_user_by_session(session)
    if not user_info:
        return EmptyPayload(), False, "Unauthenticated"
    role, username = user_info

    if role != Role.PLAYER:
        return EmptyPayload(), False, "Only players can start games"
    
    room_id = room_manager.get_room_id_by_player(username)
    if not room_id:
        return EmptyPayload(), False, "Not in a room"
    
    room = room_manager.get_room_by_room_id(room_id)
    if not room:
        return EmptyPayload(), False, "Room not found"
        
    if room.host != username:
        return EmptyPayload(), False, "Only host can start game"
        
    if room.status != RoomStatus.WAITING:
        return EmptyPayload(), False, "Game already started or room not ready"
        
    game_info = db.get_game(room.game_name)
    if not game_info:
        return EmptyPayload(), False, "Game not found"
        
    # game_info: (name, developer, version, min_players, max_players, client_zip_sha256, client_folder_sha256, file_path)
    min_players = game_info[3]
    if len(room.player_list) < min_players:
        return EmptyPayload(), False, f"Not enough players (min {min_players})"
    
    max_players = game_info[4]
    if len(room.player_list) > max_players:
        return EmptyPayload(), False, f"Too many players (max {max_players})"
        
    game_file_path = game_info[7]
    server_zip_path = os.path.join(game_file_path, "server.zip")
    
    # Check if server zip exists
    if not os.path.exists(server_zip_path):
        return EmptyPayload(), False, "Game server files not found"
        
    room_manager.set_room_status(room_id, RoomStatus.STARTING)
    room_manager.clear_room_player_ready(room_id)
    
    # Broadcast GAME_CHECK
    game_check_event_payload = GameCheckEventPayload(
        game_name=room.game_name,
    )
    game_check_msg = Message.event(Action.GAME_CHECK, game_check_event_payload)
    broadcaster.multicast_to_players(session_user_map, game_check_msg, usernames=room.player_list)

    # Broadcast room update
    room_update_event_payload = RoomUpdatedEventPayload(
        room_id=room_id,
        host_username=room.host,
        game_name=room.game_name,
        current_players=len(room.player_list),
        max_players=room.max_players,
        status=room.status.value
    )
    room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
    broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)
    
    return EmptyPayload(), True, ""

def _on_game_end(room_id: str, room_manager: RoomManager, session_user_map: SessionUserMap):
    logger.info(f"Handling game end for room {room_id}.")
    room = room_manager.get_room_by_room_id(room_id)
    if not room:
        logger.warning(f"Room {room_id} not found during game end handling")
        return

    # Reset room state
    # room.status = RoomStatus.WAITING
    # room.ready_player_set.clear()
    room_manager.set_room_status(room_id, RoomStatus.WAITING)
    room_manager.clear_room_player_ready(room_id)

    # Notify all players in lobby (RoomUpdated)
    # The room status changed from IN_GAME to WAITING
    room_update_event_payload = RoomUpdatedEventPayload(
        room_id=room_id,
        host_username=room.host,
        game_name=room.game_name,
        current_players=len(room.player_list),
        max_players=room.max_players,
        status=room.status.value
    )
    room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
    broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)

    # Notify players inside the room (MyRoomUpdated)
    # They should transition back to room view
    my_room_payload = MyRoomUpdatedEventPayload(
        host_username=room.host,
        game_name=room.game_name,
        player_list=room.player_list,
        max_players=room.max_players,
        status=room.status.value,
    )
    my_room_msg = Message.event(Action.MY_ROOM_UPDATED, my_room_payload)
    broadcaster.multicast_to_players(session_user_map, my_room_msg, usernames=room.player_list)


def handle_game_check_result(payload: GameCheckResultPayload, room_manager: RoomManager, game_process_manager: GameProcessManager, db: Database, session_user_map: SessionUserMap, session: Session) -> tuple[EmptyPayload, bool, str]:
    user_info = session_user_map.get_user_by_session(session)
    if not user_info:
         return EmptyPayload(), False, "Unauthenticated"
    role, username = user_info

    if role != Role.PLAYER:
        return EmptyPayload(), False, "Only players can send game check result"
    
    room_id = room_manager.get_room_id_by_player(username)
    if not room_id:
        return EmptyPayload(), False, "Not in a room"
        
    room = room_manager.get_room_by_room_id(room_id)
    if not room or room.status != RoomStatus.STARTING:
        return EmptyPayload(), False, "Room not in launching state"
    
    game_info = db.get_game(room.game_name)
    if not game_info:
        return EmptyPayload(), False, "Game not found"
    
    # game_info: (name, developer, version, min_players, max_players, client_zip_sha256, client_folder_sha256, file_path)
    expected_version = game_info[2]  # version
    if payload.version != expected_version:
        room_manager.set_room_status(room_id, RoomStatus.WAITING)
        room_manager.clear_room_player_ready(room_id)
        room_update_event_payload = RoomUpdatedEventPayload(
            room_id=room_id,
            host_username=room.host,
            game_name=room.game_name,
            current_players=len(room.player_list),
            max_players=room.max_players,
            status=room.status.value
        )
        room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
        broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)
        return EmptyPayload(), False, f"Game version mismatch for user {username}"

    expected_sha256 = game_info[6]  # client_folder_sha256
    if payload.sha256 != expected_sha256:
        room_manager.set_room_status(room_id, RoomStatus.WAITING)
        room_manager.clear_room_player_ready(room_id)
        room_update_event_payload = RoomUpdatedEventPayload(
            room_id=room_id,
            host_username=room.host,
            game_name=room.game_name,
            current_players=len(room.player_list),
            max_players=room.max_players,
            status=room.status.value
        )
        room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
        broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)
        return EmptyPayload(), False, f"Game integrity check failed for user {username}"

    # Mark player as ready
    room_manager.add_room_player_ready(room_id, username)
    logger.info(f"User {username} ready for game in room {room_id}. ({len(room.ready_player_set)}/{len(room.player_list)})")

    if room_manager.is_player_all_ready(room_id):
        # Check if port is already allocated or process running (safeguard)
        # Note: Accessing private member _running_processes is not ideal but effective for this check
        if room_id in game_process_manager._running_processes:
             logger.warning(f"Game process already running for room {room_id}, skipping start.")
             return EmptyPayload(), True, ""

        game_file_path = game_info[7]
        server_zip_path = os.path.join(game_file_path, "server.zip")

        # Check if server zip exists
        if not os.path.exists(server_zip_path):
            room_manager.set_room_status(room_id, RoomStatus.WAITING)
            room_manager.clear_room_player_ready(room_id)
            room_update_event_payload = RoomUpdatedEventPayload(
                room_id=room_id,
                host_username=room.host,
                game_name=room.game_name,
                current_players=len(room.player_list),
                max_players=room.max_players,
                status=room.status.value
            )
            room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
            broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)
            return EmptyPayload(), False, "Game server files not found"

        def _on_game_end_wrapper(rid: str):
            _on_game_end(rid, room_manager, session_user_map)

        success, port, error = game_process_manager.start_game_server(room_id, server_zip_path, on_game_end=_on_game_end_wrapper)
        if not success:
            room_manager.set_room_status(room_id, RoomStatus.WAITING)
            room_manager.clear_room_player_ready(room_id)
            room_update_event_payload = RoomUpdatedEventPayload(
                room_id=room_id,
                host_username=room.host,
                game_name=room.game_name,
                current_players=len(room.player_list),
                max_players=room.max_players,
                status=room.status.value
            )
            room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
            broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)
            return EmptyPayload(), False, f"Failed to start server: {error}"
        
        # All ready, Broadcast GAME_START_RESULT
             
        room_manager.set_room_status(room_id, RoomStatus.IN_GAME)
        
        game_start_result_event_payload = GameStartResultEventPayload(
            game_name=room.game_name,
            port=port
        )
        game_start_result_msg = Message.event(Action.GAME_START_RESULT, game_start_result_event_payload, ok=True)
        broadcaster.multicast_to_players(session_user_map, game_start_result_msg, usernames=room.player_list)

        # Broadcast room update
        room_update_event_payload = RoomUpdatedEventPayload(
            room_id=room_id,
            host_username=room.host,
            game_name=room.game_name,
            current_players=len(room.player_list),
            max_players=room.max_players,
            status=room.status.value
        )
        room_update_msg = Message.event(Action.ROOM_UPDATED, room_update_event_payload)
        broadcaster.broadcast_to_players(session_user_map, room_update_msg, exclude_usernames=room.player_list)

        logger.info(f"Game started for room {room_id} on port {port}")
    
    return EmptyPayload(), True, ""