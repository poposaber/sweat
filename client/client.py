import logging
from client.infra.connector import Connector
from client.infra.library_manager import LibraryManager
from session.session import Session
from client.api import auth, game
from protocol.payloads import game as game_payloads
import os

NORMAL_TIMEOUT = 3.0  # seconds

class Client:
    def __init__(self, addr: tuple[str, int], trace_io: bool = False) -> None:
        self._addr = addr
        self._connector = Connector(addr)
        self._session: Session | None = None
        self._trace_io = bool(trace_io)
        self._username: str | None = None

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

    def set_username(self, username: str) -> None:
        self._username = username

    def clear_username(self) -> None:
        self._username = None

    def get_username(self) -> str | None:
        return self._username

    def login(self, username: str, password: str, role: str) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = auth.login(self._session, username=username, password=password, role=role)
        assert resp.ok is not None
        return resp.ok, resp.error

    def logout(self) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = auth.logout(self._session)
        assert resp.ok is not None
        return resp.ok, resp.error
    
    def register(self, username: str, password: str, role: str) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = auth.register(self._session, username=username, password=password, role=role)
        assert resp.ok is not None
        return resp.ok, resp.error

    def upload_game(self, name: str, version: str, min_players: int, max_players: int, file_path: str, progress_callback=None) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game.upload_game(self._session, name, version, min_players, max_players, file_path, progress_callback)
        assert resp.ok is not None
        return resp.ok, resp.error
    
    def fetch_my_works(self) -> tuple[bool, list[tuple[str, str, int, int]] | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game.fetch_my_works(self._session)
        if resp.ok:
            assert isinstance(resp.payload, game_payloads.FetchMyWorksResponsePayload)
            return True, resp.payload.works
        else:
            return False, resp.error
        
    def fetch_store(self, page: int, page_size: int) -> tuple[bool, tuple[list[tuple[str, str, int, int]], int] | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game.fetch_store(self._session, page, page_size)
        if resp.ok:
            assert isinstance(resp.payload, game_payloads.FetchStoreResponsePayload)
            return True, (resp.payload.games, resp.payload.total_count)
        else:
            return False, resp.error

    def fetch_game_cover(self, game_name: str) -> tuple[bool, bytes | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game.fetch_game_cover(self._session, game_name)
        if resp.ok:
            assert isinstance(resp.payload, game_payloads.FetchGameCoverResponsePayload)
            return True, resp.payload.cover_data
        else:
            return False, resp.error
        
    def fetch_game_detail(self, game_name: str) -> tuple[bool, tuple[str, str, int, int, str] | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game.fetch_game_detail(self._session, game_name)
        if resp.ok:
            assert isinstance(resp.payload, game_payloads.FetchGameDetailResponsePayload)
            return True, (resp.payload.developer, resp.payload.version, resp.payload.min_players, resp.payload.max_players, resp.payload.description)
        else:
            return False, resp.error
        
    def download_game(self, game_name: str, progress_callback=None) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        if self._username is None:
            raise RuntimeError("Username is not set in client")
        dest_folder_path = os.path.join("client", "games", self._username)
        os.makedirs(dest_folder_path, exist_ok=True)
        
        library_manager = LibraryManager(dest_folder_path)
        resp = game.download_game(self._session, game_name, dest_folder_path, library_manager, progress_callback)
        assert resp.ok is not None
        return resp.ok, resp.error