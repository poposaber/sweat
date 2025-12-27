import logging
from client.infra.connector import Connector
from session.session import Session
from client.api import auth

NORMAL_TIMEOUT = 3.0  # seconds

class Client:
    def __init__(self, addr: tuple[str, int], trace_io: bool = False) -> None:
        self._addr = addr
        self._connector = Connector(addr)
        self._session: Session | None = None
        self._trace_io = bool(trace_io)

    def connect(self, connect_timeout: float | None = None, on_event=None, on_disconnect=None):
        session = self._connector.connect(connect_timeout=connect_timeout)
        self._session = session
        self.settimeout(NORMAL_TIMEOUT)
        try:
            session.set_trace_io(self._trace_io)
        except Exception:
            pass
        self._session.start_recv_loop(on_event=on_event, on_disconnect=on_disconnect)
    
    def is_connected(self) -> bool:
        return self._session is not None
    
    def settimeout(self, timeout: float | None) -> None:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        self._session.set_send_timeout(timeout)
        self._session.set_recv_timeout(timeout)
    
    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def login(self, username: str, password: str, role: str):
        if self._session is None:
            raise RuntimeError("Client is not connected")
        return auth.login(self._session, username=username, password=password, role=role)

    def logout(self):
        if self._session is None:
            raise RuntimeError("Client is not connected")
        return auth.logout(self._session)
    
    def register(self, username: str, password: str, role: str):
        if self._session is None:
            raise RuntimeError("Client is not connected")
        return auth.register(self._session, username=username, password=password, role=role)

