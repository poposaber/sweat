import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import Any, Iterable, Callable, Optional

class FileBrowser(ctk.CTkFrame):
    def __init__(self, master: Any, width: int, height: int, filetypes: Iterable[tuple[str, str | list[str] | tuple[str, ...]]], 
                 on_browse_done: Optional[Callable[[str], None]] = None):
        super().__init__(master, width, height, fg_color="transparent")
        self._filetypes = filetypes
        self._on_browse_done = on_browse_done

        self.entry = ctk.CTkEntry(self, state="readonly")
        self.entry.place(relx=0, rely=0, relwidth=0.775, relheight=1, anchor=tk.NW)
        self._browse_btn = ctk.CTkButton(self, text="Browse", command=self.browse_file)
        self._browse_btn.place(relx=1, rely=0, relwidth=0.175, relheight=1, anchor=tk.NE)

    def browse_file(self):
        path = filedialog.askopenfilename(title="Select File", filetypes=self._filetypes)
        if path:
            self.entry.configure(state="normal")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, path)
            self.entry.configure(state="readonly")
            if self._on_browse_done:
                self._on_browse_done(path)