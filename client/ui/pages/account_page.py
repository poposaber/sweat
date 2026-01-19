import customtkinter
from typing import Callable, Optional
from tkinter import messagebox

class AccountPage(customtkinter.CTkFrame):
    def __init__(self, master, logout_callback: Optional[Callable[[], None]] = None, get_user_info_callback: Optional[Callable[[Callable[[str], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)

        # self.label = customtkinter.CTkLabel(self, text="Account Page", font=("Arial", 20))
        # self.label.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)
        self._get_user_info_callback = get_user_info_callback
        self.username_label = customtkinter.CTkLabel(self, text="Anonymous", font=("Arial", 30, "bold"))
        self.username_label.place(relx=0.1, rely=0.1, anchor=customtkinter.NW)

        self.logout_btn = customtkinter.CTkButton(self, text="Logout", width=100, height=40, command=logout_callback)
        self.logout_btn.place(relx=0.5, rely=0.6, anchor=customtkinter.CENTER)

    def update_user_info(self):
        if self._get_user_info_callback:
            self._get_user_info_callback(
                self.on_get_user_info_success,
                self.on_error
            )

    def on_get_user_info_success(self, user_name: str):
        self.username_label.configure(text=user_name)

    def on_error(self, error: Exception):
        messagebox.showerror("Error", str(error))