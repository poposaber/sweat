import logging
import threading
from typing import Optional
from server.infra.acceptor import Acceptor
from session.session import Session
from server.dispatcher import Dispatcher
from session.errors import SessionDisconnectedError
from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.room_manager import RoomManager
from protocol.enums import Role

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, addr: tuple[str, int], trace_io: bool = False):
        self._addr = addr
        self._acceptor = Acceptor(addr)
        self._db = Database()
        self._session_user_map = SessionUserMap()
        self._room_manager = RoomManager()
        self._dispatcher = Dispatcher(self._db, self._session_user_map, self._room_manager)
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []
        # self._sessions: list[Session] = []
        
        self._trace_io = bool(trace_io)

    def output_room_manager_status(self):
        self._room_manager.output_status()

    def serve(self):
        """Accept connections in a loop and handle each in a dedicated thread."""
        logger.info("Server listening on %s:%d", self._addr[0], self._addr[1])
        while not self._stop_event.is_set():
            try:
                session, addr = self._acceptor.accept()
                try:
                    session.set_trace_io(self._trace_io)
                except Exception:
                    pass
                logger.info("Accepted connection from %s:%d", addr[0], addr[1])
            except Exception:
                if self._stop_event.is_set():
                    break
                logger.exception("Accept failed")
                continue
            t = threading.Thread(target=self._client_loop, args=(session, addr), daemon=True)
            self._threads.append(t)
            self._session_user_map.add_session(session)
            t.start()

    def _client_loop(self, session: Session, addr: Optional[tuple[str, int]] = None):
        """Per-connection loop: receive, dispatch, respond until error or stop."""
        try:
            while not self._stop_event.is_set():
                try:
                    req = session.receive_message()
                    resp = self._dispatcher.dispatch(req, session)
                    session.send_message(resp)
                except Exception as e:
                    # 正常斷線：降低為 info，其他錯誤保留堆疊
                    if isinstance(e, SessionDisconnectedError):
                        if addr:
                            logger.info(f"Client {addr[0]}:{addr[1]} disconnected")
                        else:
                            logger.info("Client disconnected")
                    else:
                        if addr:
                            logger.exception(f"Client {addr[0]}:{addr[1]} handler error: {e}")
                        else:
                            logger.exception(f"Client handler error: {e}")
                    break
        finally:
            self._cleanup_session(session)

    def _cleanup_session(self, session: Session):
        userinfo = self._session_user_map.get_user_by_session(session)
        if userinfo:
            role, username = userinfo
            logger.info(f"Cleaning up session for user={username}, role={role}")
            if role == Role.PLAYER:
                room_id = self._room_manager.get_room_id_by_player(username)
                if room_id:
                    self._room_manager.remove_player_from_room(room_id, username)
                    logger.info(f"User {username} removed from room {room_id} on session cleanup")
        self._session_user_map.remove_session(session)
        try:
            session.close()
        except Exception:
            logger.exception("Failed to close session in client loop")

    def close(self):
        self.stop()

    def stop(self):
        """Signal server to stop, close acceptor, and join threads."""
        self._stop_event.set()
        try:
            self._acceptor.close()  # this should unblock accept
        except Exception:
            logger.exception("Error closing acceptor")
        for session in self._session_user_map.get_all_sessions():
            try:
                session.close()
            except Exception:
                logger.exception("Error closing session")
        self._session_user_map.clear_all()
        
        for t in list(self._threads):
            try:
                t.join(timeout=1.0)
            except Exception:
                pass
        self._threads.clear()
