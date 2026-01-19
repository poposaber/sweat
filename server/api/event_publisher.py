import logging
from protocol.payloads.events import RoomRemovedEventPayload, RoomUpdatedEventPayload, MyRoomUpdatedEventPayload, UsernameEventPayload
from protocol.enums import Action
from protocol.message import Message
from server.infra.room_manager import RoomManager
from server.infra.session_user_map import SessionUserMap
import server.infra.broadcaster as broadcaster

logger = logging.getLogger(__name__)

def broadcast_leave_room_event(room_manager: RoomManager, session_user_map: SessionUserMap, username: str, room_id: str):
    """
    Broadcasts room updates after a user has left a room.
    Assumes the user has ALREADY been removed from the room manager.
    """
    # check if the room still exists after player leaves
    room = room_manager.get_room_by_room_id(room_id)
    if not room:
        # room deleted, send room removed event
        event_payload = RoomRemovedEventPayload(
            room_id=room_id
        )
        msg_event = Message.event(Action.ROOM_REMOVED, event_payload)
        broadcaster.broadcast_to_players(session_user_map, msg_event, exclude_usernames=[username])
        logger.info(f"Room {room_id} removed event broadcasted (last user {username} left)")
    else:
        # room still exists, send room updated event to players not in that room and send my room updated event to players in that room
        room_updated_event_payload = RoomUpdatedEventPayload(
            room_id=room_id, 
            host_username=room.host, 
            game_name=room.game_name, 
            current_players=len(room.player_list), 
            max_players=room.max_players, 
            status=room.status.value
        )
        my_room_updated_event_payload = MyRoomUpdatedEventPayload(
            host_username=room.host, 
            game_name=room.game_name, 
            player_list=room.player_list.copy(), 
            max_players=room.max_players, 
            status=room.status.value
        )
        
        msg_room_updated_event = Message.event(Action.ROOM_UPDATED, room_updated_event_payload)
        msg_my_room_updated_event = Message.event(Action.MY_ROOM_UPDATED, my_room_updated_event_payload)
        
        # 1. Update players inside the room (Multicast)
        broadcaster.multicast_to_players(session_user_map, msg_my_room_updated_event, room.player_list)

        # 2. Update everyone else in the lobby (Broadcast excluding room members + the leaver)
        # The leaver (username) is already removed from room.player_list, so we need to exclude:
        # - Leaver [username]
        # - Current Members [room.player_list]
        exclude_list = [username] + room.player_list
        broadcaster.broadcast_to_players(session_user_map, msg_room_updated_event, exclude_usernames=exclude_list)
        logger.info(f"Room {room_id} updated event broadcasted (user {username} left)")

def broadcast_join_room_event(room_manager: RoomManager, session_user_map: SessionUserMap, username: str, room_id: str):
    """
    Broadcasts room updates after a user has joined a room.
    Assumes the user has ALREADY been added to the room manager.
    """
    room = room_manager.get_room_by_room_id(room_id)
    if not room:
        logger.warning(f"Broadcast join room event failed: room_id={room_id} not found for user={username}")
        return
    
    # room exists, send room updated event to players not in that room and send my room updated event to players in that room
    room_updated_event_payload = RoomUpdatedEventPayload(
        room_id=room_id, 
        host_username=room.host, 
        game_name=room.game_name, 
        current_players=len(room.player_list), 
        max_players=room.max_players, 
        status=room.status.value
    )
    my_room_updated_event_payload = MyRoomUpdatedEventPayload(
        host_username=room.host, 
        game_name=room.game_name, 
        player_list=room.player_list.copy(), 
        max_players=room.max_players, 
        status=room.status.value
    )
    
    msg_room_updated_event = Message.event(Action.ROOM_UPDATED, room_updated_event_payload)
    msg_my_room_updated_event = Message.event(Action.MY_ROOM_UPDATED, my_room_updated_event_payload)
    
    # 1. Update players inside the room (Multicast)
    broadcaster.multicast_to_players(session_user_map, msg_my_room_updated_event, room.player_list)

    # 2. Update everyone else in the lobby (Broadcast excluding room members)
    exclude_list = room.player_list.copy()  # includes the new joiner
    broadcaster.broadcast_to_players(session_user_map, msg_room_updated_event, exclude_usernames=exclude_list)
    logger.info(f"Room {room_id} updated event broadcasted (user {username} joined)")

def broadcast_player_logged_out_event(session_user_map: SessionUserMap, username: str):
    """
    Broadcasts a player logged out event to all players except the one who logged out.
    """
    event_payload = UsernameEventPayload(
        username=username
    )
    msg_event = Message.event(Action.PLAYER_LOGGED_OUT, event_payload)
    broadcaster.broadcast_to_players(session_user_map, msg_event, exclude_usernames=[username])
    logger.info(f"Player logged out event broadcasted for user {username}")

def broadcast_player_logged_in_event(session_user_map: SessionUserMap, username: str):
    """
    Broadcasts a player logged in event to all players except the one who logged in.
    """
    event_payload = UsernameEventPayload(
        username=username
    )
    msg_event = Message.event(Action.PLAYER_LOGGED_IN, event_payload)
    broadcaster.broadcast_to_players(session_user_map, msg_event, exclude_usernames=[username])
    logger.info(f"Player logged in event broadcasted for user {username}")
