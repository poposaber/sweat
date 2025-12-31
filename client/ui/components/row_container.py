import customtkinter
from typing import Callable, Optional

class RowContainer(customtkinter.CTkScrollableFrame):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self._current_row = 0

    def add_row(self, widget: customtkinter.CTkFrame):
        # widget.configure(master=self)
        widget.grid(row=self._current_row, column=0, sticky=customtkinter.EW, padx=5, pady=5)
        self._current_row += 1

    def clear_rows(self):
        for child in self.winfo_children():
            child.destroy()
        self._current_row = 0