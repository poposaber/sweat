import customtkinter
from typing import Callable, Optional

class ClickableRow(customtkinter.CTkFrame):
    def __init__(self, master, height: int = 30, command: Optional[Callable[[], None]] = None, **kwargs):
        self.command = command
        super().__init__(master, height=height, **kwargs)
        if self.command is not None:
            c = self.command
            self.bind("<Button-1>", lambda e: c())

