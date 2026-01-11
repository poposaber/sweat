from typing import List, Optional
from protocol.enums import Role
from protocol.message import Message
from server.infra.session_user_map import SessionUserMap

def broadcast_to_players(session_user_map: SessionUserMap, message: Message, exclude_usernames: Optional[List[str]] = None):
    """
    Send a message to all connected players, optionally excluding some usernames.
    """
    if exclude_usernames is None:
        exclude_usernames = []
    
    exclude_set = set(exclude_usernames)
    
    for s in session_user_map.get_all_player_sessions():
        user_info = session_user_map.get_user_by_session(s)
        if not user_info:
             continue
        
        role, username = user_info
        # Double check role, though get_all_player_sessions should only return players
        if role == Role.PLAYER and username not in exclude_set:
            s.send_message(message)

def multicast_to_players(session_user_map: SessionUserMap, message: Message, usernames: List[str]):
    """
    Send a message to a specific list of players.
    """
    for username in usernames:
        s = session_user_map.get_session_by_user(Role.PLAYER, username)
        if s:
            s.send_message(message)
