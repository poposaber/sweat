import customtkinter
from typing import Callable, Optional
import tkinter

class LoginPage(customtkinter.CTkFrame):
    def __init__(self, master, login_callback: Optional[Callable[[str, str], None]] = None):
        super().__init__(master, width=350, height=400)
        self.login_callback = login_callback
        self.login_text = customtkinter.CTkLabel(master=self, text="Login", font=("Arial", 25, "bold"))
        self.login_text.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
        self.login_username_inputbox = customtkinter.CTkEntry(master=self, placeholder_text="Username", width=200, height=40)
        self.login_username_inputbox.bind("<Return>", lambda e: self.login_password_inputbox.focus())
        self.login_username_inputbox.bind("<Down>", lambda e: self.login_password_inputbox.focus())
        self.login_username_inputbox.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
        self.login_password_inputbox = customtkinter.CTkEntry(master=self, placeholder_text="Password", show=u"\u2022", width=200, height=40)
        self.login_password_inputbox.bind("<Return>", lambda e: self.login())
        self.login_password_inputbox.bind("<Up>", lambda e: self.login_username_inputbox.focus())
        self.login_password_inputbox.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
        self.login_error_label = customtkinter.CTkLabel(master=self, text="", font=("Arial", 15), text_color="red")
        self.login_error_label.place(relx=0.5, rely=0.7, anchor=tkinter.CENTER)
        self.login_btn = customtkinter.CTkButton(self, text="Login", width=100, height=40, command=self.login)
        self.login_btn.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)

    def login(self):
        username = self.login_username_inputbox.get()
        password = self.login_password_inputbox.get()
        if not username or not password:
            self.set_error("Username and password are required")
            return
        self.set_error("")
        if self.login_callback:
            self.login_callback(username, password)

    def set_error(self, message: str):
        self.login_error_label.configure(text=message)

    def set_credentials(self, username: str = "", password: str = ""):
        self.login_username_inputbox.delete(0, tkinter.END)
        self.login_username_inputbox.insert(0, username)
        self.login_password_inputbox.delete(0, tkinter.END)
        self.login_password_inputbox.insert(0, password)