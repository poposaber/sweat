import customtkinter
from typing import Callable, Optional

class BlockContainer(customtkinter.CTkScrollableFrame):
    def __init__(self, master, width: int = 400, height: int = 300, columns: int = 5):
        super().__init__(master, width=width, height=height, fg_color="transparent")
        self._current_row = 0
        self._columns = columns
        self._current_column = 0
        self.grid_columnconfigure(tuple(range(columns)), weight=1, uniform="columns")

    def add_block(self, widget_or_class, *args, **kwargs):
        """
        Adds a block to the container.
        Can accept an existing widget instance OR a widget class.
        If a class is provided, it will be instantiated with 'self' as master.
        """
        if isinstance(widget_or_class, type):
            widget = widget_or_class(self, *args, **kwargs)
        else:
            widget = widget_or_class

        # widget.configure(master=self)
        widget.grid(row=self._current_row, column=self._current_column, sticky=customtkinter.EW, padx=5, pady=5)
        self._current_column += 1
        if self._current_column >= self._columns:
            self._current_column = 0
            self._current_row += 1
        return widget

    def clear_blocks(self):
        for child in self.winfo_children():
            child.destroy()
        self._current_row = 0
        self._current_column = 0