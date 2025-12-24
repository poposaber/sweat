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

    def login(self, username: str, password: str,
              on_result: Optional[Callable[[], None]] = None,
              on_error: Optional[Callable[[Exception], None]] = None):
        def _work():
            try:
                self._client.login(username, password)
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
            