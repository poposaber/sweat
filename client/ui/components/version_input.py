import customtkinter as ctk
import tkinter as tk
from .uint_entry import UIntEntry

class VersionInput(ctk.CTkFrame):
    def __init__(self, master, width: int = 200, height: int = 30):
        super().__init__(master, width=width, height=height, fg_color="transparent")

        self.major_entry = UIntEntry(self, text="0")
        self.major_entry.place(relx=1/6, rely=0.5, relwidth=1/4, relheight=1, anchor=tk.CENTER)

        self.dot_label1 = ctk.CTkLabel(self, text=".")
        self.dot_label1.place(relx=1/3, rely=0.5, anchor=tk.CENTER)

        self.minor_entry = UIntEntry(self, text="0")
        self.minor_entry.place(relx=1/2, rely=0.5, relwidth=1/4, relheight=1, anchor=tk.CENTER)

        self.dot_label2 = ctk.CTkLabel(self, text=".")
        self.dot_label2.place(relx=2/3, rely=0.5, anchor=tk.CENTER)

        self.patch_entry = UIntEntry(self, text="0")
        self.patch_entry.place(relx=5/6, rely=0.5, relwidth=1/4, relheight=1, anchor=tk.CENTER)

    def get_version(self) -> str:
        return f"{self.major_entry.get()}.{self.minor_entry.get()}.{self.patch_entry.get()}"
    
    def is_valid(self) -> bool:
        return (self.major_entry.get().isdigit() and
                self.minor_entry.get().isdigit() and
                self.patch_entry.get().isdigit())
    
    

        # self.entry = ctk.CTkEntry(self)
        # self.entry.place(relx=0, rely=0, relwidth=1, relheight=1, anchor=tk.NW)