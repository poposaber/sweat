from .client import Client
from customtkinter import CTk
from typing import Callable, Optional
import threading
import logging
from protocol.enums import Role
from protocol.message import Message

logger = logging.getLogger(__name__)

class ClientController:
    def __init__(self, addr: tuple[str, int], gui: Optional[CTk] = None, trace_io: bool = False):
        self._client = Client(addr, trace_io=trace_io)
        self._gui = gui

    def set_gui(self, gui: CTk):
        """Bind the GUI instance after construction to resolve init ordering."""
        self._gui = gui

    def get_library_manager(self):
        return self._client.get_library_manager()
    
    def _on_exception(self, e: Exception, on_error: Optional[Callable[[Exception], None]] = None):
        logger.exception(f"ClientController exception: {str(e)}")
        if on_error:
            if self._gui:
                self._gui.after(0, lambda err=e, cb=on_error: cb(err))
            else:
                on_error(e)

    def connect(self, *, on_result: Optional[Callable[[], None]] = None, on_error: Optional[Callable[[Exception], None]] = None,
                start_events: bool = True, on_event: Optional[Callable[[Message], None]] = None, on_disconnect: Optional[Callable[[], None]] = None):
        
        # Wrap on_disconnect to run on GUI thread if GUI exists
        safe_on_disconnect = on_disconnect
        if self._gui and on_disconnect:
            g = self._gui
            safe_on_disconnect = lambda: g.after(0, on_disconnect)

        def _work():
            try:
                self._client.connect(on_event=on_event, on_disconnect=safe_on_disconnect)
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def login(self, username: str, password: str, role: str,
              on_result: Optional[Callable[[], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, error = self._client.login(username, password, role)
                if not success:
                    raise Exception(error or "Login failed")
                
                cb_ok = on_result
                if cb_ok:
                    self._client.set_username(username)
                    if role == Role.PLAYER.value:
                        self._client.set_library_manager_by_username(username)
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def register(self, username: str, password: str, role: str,
              on_result: Optional[Callable[[], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, error = self._client.register(username, password, role)
                if not success:
                    raise Exception(error or "Registration failed")

                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def upload_game(self, name: str, version: str, min_players: int, max_players: int, file_path: str,
                    on_result: Optional[Callable[[], None]] = None,
                    on_error: Optional[Callable[[str], None]] = None,
                    on_progress: Optional[Callable[[int, int], None]] = None):
        def _work():
            try:
                # We need to wrap on_progress to run on GUI thread if needed
                safe_progress = None
                if on_progress and self._gui:
                    g = self._gui
                    op = on_progress
                    def _p(c, t):
                        g.after(0, lambda: op(c, t))
                    safe_progress = _p
                else:
                    safe_progress = on_progress

                success, error = self._client.upload_game(name, version, min_players, max_players, file_path, safe_progress)
                if not success:
                    raise Exception(error or "Upload failed")
                
                if on_result:
                    o_r = on_result
                    if self._gui:
                        self._gui.after(0, lambda: o_r())
                    else:
                        o_r()

            except Exception as e:
                if on_error:
                    o_e = on_error
                    err_msg = str(e)
                    if self._gui:
                        self._gui.after(0, lambda: o_e(err_msg))
                    else:
                        o_e(err_msg)
        
        threading.Thread(target=_work, daemon=True).start()

    def fetch_store(self, page: int, page_size: int, 
                    on_result: Optional[Callable[[list[tuple[str, str, int, int]], int], None]] = None, 
                    on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.fetch_store(page, page_size)
                if not success:
                    raise Exception(result or "Fetch Store failed")
                
                assert isinstance(result, tuple)
                games, total_count = result
                
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(games, total_count))
                    else:
                        cb_ok(games, total_count)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def fetch_my_works(self, on_result: Optional[Callable[[list[tuple[str, str, int, int]]], None]] = None, 
                on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.fetch_my_works()
                if not success:
                    raise Exception(result or "Fetch My Works failed")
                
                assert isinstance(result, list)
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(result))
                    else:
                        cb_ok(result)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def fetch_game_cover(self, game_name: str, 
                         on_result: Optional[Callable[[bytes], None]] = None, 
                         on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.fetch_game_cover(game_name)
                if not success:
                    # It's okay if cover is missing, just return empty bytes or handle gracefully
                    # But here we treat failure as error if protocol failed
                    raise Exception(result or "Fetch Game Cover failed")
                
                assert isinstance(result, bytes)
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(result))
                    else:
                        cb_ok(result)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def fetch_game_detail(self, game_name: str, 
                          on_result: Optional[Callable[[str, str, int, int, str], None]] = None, 
                          on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.fetch_game_detail(game_name)
                if not success:
                    raise Exception(result or "Fetch Game Detail failed")
                
                assert isinstance(result, tuple)
                developer, version, min_players, max_players, description = result
                
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(developer, version, min_players, max_players, description))
                    else:
                        cb_ok(developer, version, min_players, max_players, description)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def download_game(self, game_name: str, 
                      on_result: Optional[Callable[[], None]] = None,
                      on_error: Optional[Callable[[Exception], None]] = None,
                      on_progress: Optional[Callable[[int, int], None]] = None):
        def _work():
            try:
                # We need to wrap on_progress to run on GUI thread if needed
                safe_progress = None
                if on_progress and self._gui:
                    g = self._gui
                    op = on_progress
                    def _p(c, t):
                        g.after(0, lambda: op(c, t))
                    safe_progress = _p
                else:
                    safe_progress = on_progress

                success, error = self._client.download_game(game_name, safe_progress)
                if not success:
                    raise Exception(error or "Download failed")
                
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def create_room(self, game_name: str, 
                    on_result: Optional[Callable[[str], None]] = None,
                    on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.create_room(game_name)
                if not success:
                    raise Exception(result or "Create Room failed")
                
                assert isinstance(result, str)  # room_id
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(result))
                    else:
                        cb_ok(result)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def check_my_room(self, 
                      on_result: Optional[Callable[[bool, str, str, str, list[str], str], None]] = None,
                      on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.check_my_room()
                if not success:
                    raise Exception(result or "Check My Room failed")
                
                assert isinstance(result, tuple)
                in_room, room_id, game_name, host, players, username = result
                
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(in_room, room_id, game_name, host, players, username))
                    else:
                        cb_ok(in_room, room_id, game_name, host, players, username)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()
        
    def fetch_room_list(self, 
                        on_result: Optional[Callable[[list[tuple[str, str, str, int, str]]], None]] = None,
                        on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, result = self._client.fetch_room_list()
                if not success:
                    raise Exception(result or "Fetch Room List failed")
                
                assert isinstance(result, list)
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, lambda: cb_ok(result))
                    else:
                        cb_ok(result)
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def logout(self, on_result: Optional[Callable[[], None]] = None,
               on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                success, error = self._client.logout()
                if not success:
                    raise Exception(error or "Logout failed")
                cb_ok = on_result
                if cb_ok:
                    self._client.clear_username()
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                self._on_exception(e, on_error)
        threading.Thread(target=_work, daemon=True).start()

    def close(self):
        try:
            self._client.close()
        except Exception:
            logger.exception("ClientController.close failed")
            