from session.session import Session
from .bijection_map import BijectionMap
from protocol.enums import Role
import threading

class SessionUserMap:
    def __init__(self):
        self._session_indeterminate: set[Session] = set()
        self._session_indeterminate_lock = threading.Lock()

        self._role_bijection_map: dict[Role, BijectionMap[Session, str]] = {
            Role.PLAYER: BijectionMap(),
            Role.DEVELOPER: BijectionMap(),
        }

    def add_session(self, session: Session):
        with self._session_indeterminate_lock:
            self._session_indeterminate.add(session)

    def remove_session(self, session: Session):
        with self._session_indeterminate_lock:
            if session in self._session_indeterminate:
                self._session_indeterminate.discard(session)
                return

        for bmap in self._role_bijection_map.values():
            if bmap.get_by_key1(session):
                bmap.remove_by_key1(session)
                return
    def move_session_to_user(self, session: Session, role: Role, username: str):
        with self._session_indeterminate_lock:
            self._session_indeterminate.remove(session) # raise KeyError if not present
        
        self._role_bijection_map[role].add(session, username)

    def move_session_back(self, session: Session):
        # Find which role it belongs to
        found = False
        for bmap in self._role_bijection_map.values():
            if bmap.get_by_key1(session):
                bmap.remove_by_key1(session)
                found = True
                break
        
        if found:
            with self._session_indeterminate_lock:
                self._session_indeterminate.add(session)

    def get_session_by_user(self, role: Role, username: str) -> Session | None:
        return self._role_bijection_map[role].get_by_key2(username)
        
    def get_user_by_session(self, session: Session) -> tuple[Role, str] | None:
        for role, bmap in self._role_bijection_map.items():
            username = bmap.get_by_key1(session)
            if username:
                return role, username
        return None

    def get_all_sessions(self) -> list[Session]:
        sessions = []
        with self._session_indeterminate_lock:
            sessions.extend(self._session_indeterminate)
        for bmap in self._role_bijection_map.values():
            sessions.extend(bmap.get_all_key1s())
        return sessions
        
    def clear_all(self):
        with self._session_indeterminate_lock:
            self._session_indeterminate.clear()
        for bmap in self._role_bijection_map.values():
            bmap.clear()