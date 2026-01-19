import customtkinter as ctk
from typing import Callable, Optional
from enum import Enum

class DisconnectedViewState(Enum):
    DISCONNECTED = 1
    RECONNECTING = 2

class DisconnectedView(ctk.CTkFrame):
    def __init__(self, master, reconnect_callback: Optional[Callable[[], None]] = None):
        super().__init__(master)

        self._label = ctk.CTkLabel(self, text="Disconnected from server", font=("Arial", 20))
        self._label.place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

        self._reconnect_button = ctk.CTkButton(self, text="Reconnect", command=self._on_reconnect_clicked)
        self._reconnect_button.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

        self._reconnect_callback = reconnect_callback
        self._state = DisconnectedViewState.DISCONNECTED

        self.geom_size = "350x450"

    def set_state(self, state: DisconnectedViewState):
        self._state = state
        if state == DisconnectedViewState.DISCONNECTED:
            self._label.configure(text="Disconnected from server")
            self._reconnect_button.configure(state="normal", text="Reconnect")
        elif state == DisconnectedViewState.RECONNECTING:
            self._label.configure(text="Reconnecting...")
            self._reconnect_button.configure(state="disabled", text="Reconnecting...")

    def _on_reconnect_clicked(self):
        if self._reconnect_callback:
            self.set_state(DisconnectedViewState.RECONNECTING)
            self._reconnect_callback()