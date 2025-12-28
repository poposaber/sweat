import customtkinter
from typing import Callable, Optional
import tkinter

class AccountPage(customtkinter.CTkFrame):
    def __init__(self, master, logout_callback: Optional[Callable[[], None]] = None):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="Account Page", font=("Arial", 20))
        self.label.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)

        self.logout_btn = customtkinter.CTkButton(self, text="Logout", width=100, height=40, command=logout_callback)
        self.logout_btn.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)