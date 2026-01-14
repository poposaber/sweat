import logging
from protocol.payloads.common import EmptyPayload

from protocol.payloads.room import *

from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.room_manager import RoomManager
from session.session import Session
from protocol.payloads.events import RoomCreatedEventPayload
from protocol.enums import Role, Action, RoomStatus
from protocol.message import Message
import server.infra.broadcaster as broadcaster
from server.api import room_event_publisher as rep

logger = logging.getLogger(__name__)


def handle_create_room(payload: CreateRoomPayload, db: Database, room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[CreateRoomResponsePayload, bool, str]:
    addr = session.peer_address
    user_info = session_user_map.get_user_by_session(session)
    try:
        if not user_info:
            logger.warning(f"Create room failed: Unauthenticated session from addr={addr}")
            raise Exception("Unauthenticated session")
        
        role, username = user_info
        # only players can create rooms
        if role != Role.PLAYER:
            logger.warning(f"Create room failed: Unauthorized role - {role} for user={username}, addr={addr}")
            raise Exception("Only players can create rooms")
        
        logger.info(f"Create room attempt: user={username}, game={payload.game_name}, addr={addr}")

        game_info = db.get_game(payload.game_name)
        if not game_info:
            logger.warning(f"Create room failed: Game {payload.game_name} not found for user={username}, addr={addr}")
            raise Exception(f"Game {payload.game_name} not found")
        
        max_players = game_info[4]  # min_players, max_players are at index 3 and 4

        room_id = room_manager.create_room(username, payload.game_name, max_players)
        # after creating the room, send event to notify other players to update their room list
        event_payload = RoomCreatedEventPayload(
            room_id=room_id,
            host_username=username,
            game_name=payload.game_name,
            current_players=1,
            max_players=max_players,
            status=RoomStatus.WAITING.value
        )
        msg_event = Message.event(Action.ROOM_CREATED, event_payload)
        
        # Send to all players except the creator (creator gets direct response)
        broadcaster.broadcast_to_players(session_user_map, msg_event, exclude_usernames=[username])

        logger.info(f"Create room success: room_id={room_id}, host={username}")

        return CreateRoomResponsePayload(room_id=room_id), True, ""
    except Exception as e:
        return CreateRoomResponsePayload(room_id=""), False, str(e)
    
def handle_join_room(payload: JoinRoomPayload, room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[EmptyPayload, bool, str]:
    addr = session.peer_address
    user_info = session_user_map.get_user_by_session(session)
    try:
        if not user_info:
            logger.warning(f"Join room failed: Unauthenticated session from addr={addr}")
            raise Exception("Unauthenticated session")
        
        role, username = user_info

        if role != Role.PLAYER:
            logger.warning(f"Join room failed: Unauthorized role - {role} for user={username}, addr={addr}")
            raise Exception("Only players can join rooms")
        
        logger.info(f"Join room attempt: user={username}, room_id={payload.room_id}, addr={addr}")

        room_manager.add_player_to_room(payload.room_id, username)

        rep.broadcast_join_room_event(room_manager, session_user_map, username, payload.room_id)

        logger.info(f"Join room success: user={username}, joined room_id={payload.room_id}")

        return EmptyPayload(), True, ""
    except Exception as e:
        logger.error(f"Join room error: user={username}, error={str(e)}")
        return EmptyPayload(), False, str(e)
    
def handle_leave_room(room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[EmptyPayload, bool, str]:
    addr = session.peer_address
    user_info = session_user_map.get_user_by_session(session)
    try:
        if not user_info:
            logger.warning(f"Leave room failed: Unauthenticated session from addr={addr}")
            raise Exception("Unauthenticated session")
        
        role, username = user_info

        if role != Role.PLAYER:
            logger.warning(f"Leave room failed: Unauthorized role - {role} for user={username}, addr={addr}")
            raise Exception("Only players can leave rooms")
        
        logger.info(f"Leave room attempt: user={username}, addr={addr}")
        room_id = room_manager.get_room_id_by_player(username)
        if not room_id:
            logger.warning(f"Leave room failed: user={username} is not in any room, addr={addr}")
            raise Exception("You are not in any room")
        
        room_manager.remove_player_from_room(room_id, username)
        
        rep.broadcast_leave_room_event(room_manager, session_user_map, username, room_id)
            
        logger.info(f"Leave room success: user={username}, left room_id={room_id}")

        return EmptyPayload(), True, ""
    except Exception as e:
        logger.error(f"Leave room error: user={username}, error={str(e)}")
        return EmptyPayload(), False, str(e)
    
def handle_check_my_room(room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[CheckMyRoomResponsePayload, bool, str]:
    addr = session.peer_address
    user_info = session_user_map.get_user_by_session(session)
    try:
        if not user_info:
            logger.warning(f"Check my room failed: Unauthenticated session from addr={addr}")
            raise Exception("Unauthenticated session")
        
        role, username = user_info

        if role != Role.PLAYER:
            logger.warning(f"Check my room failed: Unauthorized role - {role} for user={username}, addr={addr}")
            raise Exception("Only players can check their rooms")
        
        logger.info(f"Check my room attempt: user={username}, addr={addr}")
        room_id = room_manager.get_room_id_by_player(username)
        if not room_id:
            return CheckMyRoomResponsePayload(in_room=False, room_id="", game_name="", host="", player_list=[], max_players=0, status=""), True, ""
        room = room_manager.get_room_by_room_id(room_id)
        if room:
            in_room = True
            game_name = room.game_name
            host = room.host
            players = room.player_list.copy()
            max_players = room.max_players
        else: # This is not supposed to happen
            raise Exception(f"Room not found for room_id={room_id} for user={username}")
        
        logger.info(f"Check my room success: user={username}, in_room={in_room}, room_id={room_id}")

        return CheckMyRoomResponsePayload(in_room=in_room, room_id=room_id, game_name=game_name, host=host, player_list=players, max_players=max_players, status=room.status.value), True, ""
    except Exception as e:
        logger.error(f"Check my room error: user={username}, error={str(e)}")
        return CheckMyRoomResponsePayload(in_room=False, room_id="", game_name="", host="", player_list=[], max_players=0, status=""), False, str(e)
    
def handle_fetch_room_list(room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[FetchRoomListResponsePayload, bool, str]:
    addr = session.peer_address
    user_info = session_user_map.get_user_by_session(session)
    try:
        if not user_info:
            logger.warning(f"Fetch room list failed: Unauthenticated session from addr={addr}")
            raise Exception("Unauthenticated session")
        
        role, username = user_info

        if role != Role.PLAYER:
            logger.warning(f"Fetch room list failed: Unauthorized role - {role} for user={username}, addr={addr}")
            raise Exception("Only players can fetch room list")
        
        logger.info(f"Fetch room list attempt: user={username}, addr={addr}")

        rooms = room_manager.get_all_rooms()
        room_id_of_player = room_manager.get_room_id_by_player(username)
        # Exclude the room that the player is already in
        room_list = [(room_id, room.host, room.game_name, len(room.player_list), room.max_players, room.status.value) for room_id, room in rooms.items() if room_id != room_id_of_player]

        logger.info(f"Fetch room list success: user={username}, room_count={len(room_list)}")

        return FetchRoomListResponsePayload(rooms=room_list), True, ""
    except Exception as e:
        logger.error(f"Fetch room list error: user={username}, error={str(e)}")
        return FetchRoomListResponsePayload(rooms=[]), False, str(e)

