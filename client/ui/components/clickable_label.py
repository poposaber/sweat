import customtkinter
from typing import Callable, Optional
import tkinter

NORMAL_LABEL_COLOR = "#5882ff"
HOVER_LABEL_COLOR = "#295fff"
CLICK_LABEL_COLOR = "#1f4fcc"

class ClickableLabel(customtkinter.CTkLabel):
    def __init__(self, master, text: str, font: Optional[tuple] = None, command: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, text=text, font=font, text_color=NORMAL_LABEL_COLOR, **kwargs)
        self.command = command
        if self.command is not None:
            c = self.command
            self.bind("<Button-1>", lambda e: c())
        # Change cursor on hover
        self.bind("<Enter>", lambda e: self.configure(cursor="hand2", text_color=HOVER_LABEL_COLOR))
        self.bind("<Leave>", lambda e: self.configure(cursor="", text_color=NORMAL_LABEL_COLOR))
        # Change color on press it
        self.bind("<ButtonPress-1>", lambda e: self.configure(text_color=CLICK_LABEL_COLOR))
        self.bind("<ButtonRelease-1>", lambda e: self.configure(text_color=HOVER_LABEL_COLOR))

    def set_command(self, command: Callable[[], None]):
        self.command = command
        c = self.command
        self.bind("<Button-1>", lambda e: c())

    def set_text(self, text: str):
        self.configure(text=text)