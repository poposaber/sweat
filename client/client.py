import logging
from client.infra.connector import Connector
from client.infra.library_manager import LibraryManager
from client.infra.game_launcher import GameLauncher
from session.session import Session
from client.api import auth, game, room, game_launch
from protocol.payloads import game as game_payloads
from protocol.payloads import room as room_payloads
from protocol.payloads import game_launch as game_launch_payloads
from protocol.payloads import events as event_payloads
from protocol.message import Message
from protocol.enums import Action
from typing import Callable
import os
import threading

NORMAL_TIMEOUT = 3.0  # seconds
MAX_CONNECT_ATTEMPTS = 3
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, addr: tuple[str, int], trace_io: bool = False) -> None:
        self._addr = addr
        self._connector = Connector(addr)
        self._session: Session | None = None
        self._trace_io = bool(trace_io)
        self._username: str | None = None
        self._library_manager: LibraryManager | None = None
        self._game_launcher: GameLauncher | None = None
        self._idle_check_thread: threading.Thread | None = None

    def _on_event(self, event: Message, on_other_event: Callable[[Message], None] | None, on_game_launch_error: Callable[[str], None] | None) -> None:
        match event.action:
            case Action.GAME_CHECK:
                game_check_payload: event_payloads.GameCheckEventPayload = event.payload
                # Run in thread to avoid blocking recv loop which causes deadlock when waiting for response
                threading.Thread(target=self.handle_game_check, args=(game_check_payload.game_name,), daemon=True).start()
            case Action.GAME_START_RESULT:
                game_start_result_payload: event_payloads.GameStartResultEventPayload = event.payload
                if event.ok:
                    # Launch the game
                    port = game_start_result_payload.port # Assuming the payload has port
                    # The payload might just be a dict if not parsed to dataclass yet, checking json_codec. 
                    # Assuming it is objects as per json_codec.py
                    if not self.launch_game(game_start_result_payload.game_name, port):
                        if on_game_launch_error:
                            on_game_launch_error(f"Failed to launch game: {game_start_result_payload.game_name}")
                else:
                    if on_game_launch_error:
                        on_game_launch_error(f"Game start failed: {event.error}")
            case _:
                if on_other_event:
                    on_other_event(event)

    # def _idle_check_loop(self):
    #     assert self._session is not None
    #     while self.is_connected():
    #         now = time.time()
    #         last_active = self._session.last_active_time
    #         if now - last_active > IDLE_PATIENCE:
    #             logger.info("No activity for %.1f seconds, closing session", now - last_active)
    #             self.close()
    #             break
    #         time.sleep(1.0)

    def connect(self, connect_timeout: float | None = None, on_event: Callable[[Message], None] | None = None, on_disconnect=None, on_game_launch_error: Callable[[str], None] | None = None):
        session = self._connector.connect(connect_timeout=connect_timeout, max_attempts=MAX_CONNECT_ATTEMPTS)
        self._session = session
        self.settimeout(NORMAL_TIMEOUT)
        try:
            session.set_trace_io(self._trace_io)
        except Exception:
            pass
        def on_event_wrapper(event: Message):
            self._on_event(event, on_event, on_game_launch_error)
        self._session.start_recv_loop(on_event=on_event_wrapper, on_disconnect=on_disconnect)
        self._session.start_heartbeat_loop()
    
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

    def set_library_manager_and_game_launcher_by_username(self, username: str) -> None:
        dest_folder_path = os.path.join("library", username)
        self._library_manager = LibraryManager(dest_folder_path)
        self._game_launcher = GameLauncher(dest_folder_path)

    def clear_all(self) -> None:
        self._username = None
        self._library_manager = None
        self._game_launcher = None

    def get_library_manager(self) -> LibraryManager | None:
        return self._library_manager
    
    def launch_game(self, game_name: str, port: int) -> bool:
        if not self._library_manager or not self._game_launcher:
            raise RuntimeError("Library/Launcher not initialized")
        
        info = self._library_manager.get_installed_game(game_name)
        if not info:
            return False
        
        host = self._addr[0]
            
        return self._game_launcher.launch_game(info['install_folder_name'], host, port, self._username or "")
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
        
    def download_game_and_sync_library(self, game_name: str, progress_callback=None) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        if self._username is None:
            raise RuntimeError("Username is not set in client")
        # Use the persistent library manager
        if self._library_manager is None:
            raise RuntimeError("Library manager is not initialized")
        
        dest_folder_path = self._library_manager.library_root
        self._library_manager.ensure_library_exists()
        
        # library_manager = LibraryManager(dest_folder_path)
        resp = game.download_game(self._session, game_name, dest_folder_path, self._library_manager, progress_callback)
        self._library_manager.sync_manifest_and_files()
        assert resp.ok is not None
        return resp.ok, resp.error
    
    def create_room(self, game_name: str) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = room.create_room(self._session, game_name)
        if resp.ok:
            assert isinstance(resp.payload, room_payloads.CreateRoomResponsePayload)
            return True, resp.payload.room_id
        else:
            return False, resp.error
        
    def join_room(self, room_id: str, game_name: str) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        if self._library_manager is None:
            raise RuntimeError("Library manager is not initialized")
        if not self._library_manager.get_installed_game(game_name):
            return False, "Game not installed"
        resp = room.join_room(self._session, room_id)
        assert resp.ok is not None
        return resp.ok, resp.error
        
    def leave_room(self) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = room.leave_room(self._session)
        assert resp.ok is not None
        return resp.ok, resp.error
        
    def check_my_room(self) -> tuple[bool, tuple[bool, str, str, str, list[str], int, str] | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = room.check_my_room(self._session)
        if resp.ok:
            assert isinstance(resp.payload, room_payloads.CheckMyRoomResponsePayload)
            return True, (resp.payload.in_room, resp.payload.room_id, resp.payload.game_name, resp.payload.host, resp.payload.player_list, resp.payload.max_players, resp.payload.status)
        else:
            return False, resp.error
        
    def fetch_room_list(self) -> tuple[bool, list[tuple[str, str, str, int, int, str]] | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = room.fetch_room_list(self._session)
        if resp.ok:
            assert isinstance(resp.payload, room_payloads.FetchRoomListResponsePayload)
            return True, resp.payload.rooms
        else:
            return False, resp.error
        
    def fetch_player_list(self) -> tuple[bool, list[str] | str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = room.fetch_player_list(self._session)
        if resp.ok:
            assert isinstance(resp.payload, room_payloads.FetchPlayerListResponsePayload)
            return True, resp.payload.players
        else:
            return False, resp.error
        
    def start_game(self) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game_launch.start_game(self._session)
        assert resp.ok is not None
        return resp.ok, resp.error
    
    def handle_game_check(self, game_name: str) -> None:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        if self._library_manager is None:
            raise RuntimeError("Library manager is not initialized")
        installed_game = self._library_manager.get_installed_game(game_name)
        if not installed_game:
            # Game not installed
            version = ""
            sha256 = ""
        else:
            version = installed_game["version"]
            sha256 = self._library_manager.get_installed_game_sha256(game_name) or ""
        self.send_game_check_result(game_name, version, sha256)
    
    def send_game_check_result(self, game_name: str, version: str, sha256: str) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game_launch.send_game_check_result(self._session, game_name, version, sha256)
        assert resp.ok is not None
        return resp.ok, resp.error
    
    def get_user_info(self) -> tuple[bool, str | None]:
        if self._username is None:
            return False, "Username not set"
        return True, self._username
    
    def delete_game(self, game_name: str) -> tuple[bool, str | None]:
        if self._library_manager is None:
            raise RuntimeError("Library manager is not initialized")
        self._library_manager.uninstall_game(game_name)
        return True, None
    
    def remove_game_from_server(self, game_name: str) -> tuple[bool, str | None]:
        if self._session is None:
            raise RuntimeError("Client is not connected")
        resp = game.remove_game(self._session, game_name)
        assert resp.ok is not None
        return resp.ok, resp.error