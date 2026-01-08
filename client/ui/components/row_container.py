import customtkinter
from typing import Callable, Optional

class RowContainer(customtkinter.CTkScrollableFrame):
    def __init__(self, master, width: int = 400, height: int = 300):
        super().__init__(master, width=width, height=height, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self._current_row = 0

    def add_row(self, widget_or_class, *args, **kwargs):
        """
        Adds a row to the container.
        Can accept an existing widget instance OR a widget class.
        If a class is provided, it will be instantiated with 'self' as master.
        """
        if isinstance(widget_or_class, type):
            widget = widget_or_class(self, *args, **kwargs)
        else:
            widget = widget_or_class

        # widget.configure(master=self)
        widget.grid(row=self._current_row, column=0, sticky=customtkinter.EW, padx=5, pady=5)
        self._current_row += 1
        return widget

    def clear_rows(self):
        for child in self.winfo_children():
            child.destroy()
        self._current_row = 0

    def remove_row(self, widget):
        widget.destroy()