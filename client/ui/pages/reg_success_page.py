import customtkinter
from typing import Callable, Optional
import tkinter

class RegSuccessPage(customtkinter.CTkFrame):
    def __init__(self, master, continue_callback: Optional[Callable[[], None]] = None):
        super().__init__(master, width=300, height=200, fg_color="transparent")
        self.continue_callback = continue_callback

        self.success_text = customtkinter.CTkLabel(master=self, text="Registration Successful!", font=("Arial", 20, "bold"))
        self.success_text.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)

        self.continue_btn = customtkinter.CTkButton(self, text="Continue to Login", width=150, height=40, command=self.continue_to_login)
        self.continue_btn.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

    def continue_to_login(self):
        if self.continue_callback:
            self.continue_callback()