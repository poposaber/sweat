from .client import Client
from customtkinter import CTk
from typing import Callable, Optional
import threading
import logging

logger = logging.getLogger(__name__)

class ClientController:
    def __init__(self, addr: tuple[str, int], gui: Optional[CTk] = None, trace_io: bool = False):
        self._client = Client(addr, trace_io=trace_io)
        self._gui = gui

    def set_gui(self, gui: CTk):
        """Bind the GUI instance after construction to resolve init ordering."""
        self._gui = gui

    def connect(self, *, on_result: Optional[Callable[[], None]] = None, on_error: Optional[Callable[[Exception], None]] = None,
                start_events: bool = True, on_event: Optional[Callable] = None, on_disconnect: Optional[Callable[[], None]] = None):
        
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
                cb_err = on_error
                if cb_err:
                    if self._gui:
                        self._gui.after(0, lambda err=e, cb=cb_err: cb(err))
                    else:
                        cb_err(e)
        threading.Thread(target=_work, daemon=True).start()

    def login(self, username: str, password: str, role: str,
              on_result: Optional[Callable[[], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                resp = self._client.login(username, password, role)
                if not resp.ok:
                    raise Exception(resp.error or "Login failed")
                
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                cb_err = on_error
                if cb_err:
                    if self._gui:
                        self._gui.after(0, lambda err=e, cb=cb_err: cb(err))
                    else:
                        cb_err(e)
        threading.Thread(target=_work, daemon=True).start()

    def register(self, username: str, password: str, role: str,
              on_result: Optional[Callable[[], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                resp = self._client.register(username, password, role)
                if not resp.ok:
                    raise Exception(resp.error or "Registration failed")

                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                cb_err = on_error
                if cb_err:
                    if self._gui:
                        self._gui.after(0, lambda err=e, cb=cb_err: cb(err))
                    else:
                        cb_err(e)
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

                resp = self._client.upload_game(name, version, min_players, max_players, file_path, safe_progress)
                if not resp.ok:
                    raise Exception(resp.error or "Upload failed")
                
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
        

    def logout(self, on_result: Optional[Callable[[], None]] = None,
               on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                self._client.logout()
                cb_ok = on_result
                if cb_ok:
                    if self._gui:
                        self._gui.after(0, cb_ok)
                    else:
                        cb_ok()
            except Exception as e:
                cb_err = on_error
                if cb_err:
                    if self._gui:
                        self._gui.after(0, lambda err=e, cb=cb_err: cb(err))
                    else:
                        cb_err(e)
        threading.Thread(target=_work, daemon=True).start()

    def close(self):
        try:
            self._client.close()
        except Exception:
            logger.exception("ClientController.close failed")
            