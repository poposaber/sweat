import logging
from protocol.payloads.common import EmptyPayload

from protocol.payloads.room import (CreateRoomPayload, CreateRoomResponsePayload, 
                                    LeaveRoomPayload, 
                                    CheckMyRoomResponsePayload)

from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.room_manager import RoomManager
from session.session import Session
from protocol.enums import Role

logger = logging.getLogger(__name__)

def handle_create_room(payload: CreateRoomPayload, room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[CreateRoomResponsePayload, bool, str]:
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

        room_id = room_manager.create_room(username, payload.game_name)
        
        logger.info(f"Create room success: room_id={room_id}, host={username}")

        return CreateRoomResponsePayload(room_id=room_id), True, ""
    except Exception as e:
        return CreateRoomResponsePayload(room_id=""), False, str(e)
    
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
            return CheckMyRoomResponsePayload(in_room=False, room_id="", game_name="", host="", players=[]), True, ""
        room = room_manager.get_room_by_room_id(room_id)
        if room:
            in_room = True
            game_name = room.game_name
            host = room.host
            players = room.players.copy()
        else: # This is not supposed to happen
            raise Exception(f"Room not found for room_id={room_id} for user={username}")
        
        logger.info(f"Check my room success: user={username}, in_room={in_room}, room_id={room_id}")

        return CheckMyRoomResponsePayload(in_room=in_room, room_id=room_id, game_name=game_name, host=host, players=players), True, ""
    except Exception as e:
        logger.error(f"Check my room error: user={username}, error={str(e)}")
        return CheckMyRoomResponsePayload(in_room=False, room_id="", game_name="", host="", players=[]), False, str(e)