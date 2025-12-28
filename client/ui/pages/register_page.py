import customtkinter
from typing import Callable, Optional
import tkinter
from protocol.enums import Role

class RegisterPage(customtkinter.CTkFrame):
    def __init__(self, master, register_callback: Optional[Callable[[str, str, str], None]] = None):
        super().__init__(master, width=350, height=450, fg_color="transparent")
        self.register_callback = register_callback

        self.reg_text = customtkinter.CTkLabel(master=self, text="Register", font=("Arial", 25, "bold"))
        self.reg_text.place(relx=0.5, rely=0.15, anchor=tkinter.CENTER)

        self.reg_username_inputbox = customtkinter.CTkEntry(master=self, placeholder_text="Username", width=200, height=40)
        self.reg_username_inputbox.bind("<Return>", lambda e: self.reg_password_inputbox.focus())
        self.reg_username_inputbox.bind("<Down>", lambda e: self.reg_password_inputbox.focus())
        self.reg_username_inputbox.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)

        self.reg_password_inputbox = customtkinter.CTkEntry(master=self, placeholder_text="Password", show=u"\u2022", width=200, height=40)
        self.reg_password_inputbox.bind("<Return>", lambda e: self.reg_confirm_password_inputbox.focus())
        self.reg_password_inputbox.bind("<Up>", lambda e: self.reg_username_inputbox.focus())
        self.reg_password_inputbox.bind("<Down>", lambda e: self.reg_confirm_password_inputbox.focus())
        self.reg_password_inputbox.place(relx=0.5, rely=0.45, anchor=tkinter.CENTER)

        self.reg_confirm_password_inputbox = customtkinter.CTkEntry(master=self, placeholder_text="Confirm password", show=u"\u2022", width=200, height=40)
        self.reg_confirm_password_inputbox.bind("<Return>", lambda e: self.register())
        self.reg_confirm_password_inputbox.bind("<Up>", lambda e: self.reg_password_inputbox.focus())
        self.reg_confirm_password_inputbox.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

        self.role_var = customtkinter.StringVar(value=Role.PLAYER.value)
        self.role_switch = customtkinter.CTkSwitch(master=self, text="Developer Mode", variable=self.role_var, onvalue=Role.DEVELOPER.value, offvalue=Role.PLAYER.value)
        self.role_switch.place(relx=0.5, rely=0.72, anchor=tkinter.CENTER)

        self.reg_error_label = customtkinter.CTkLabel(master=self, text="", font=("Arial", 15), text_color="red")
        self.reg_error_label.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)

        self.reg_btn = customtkinter.CTkButton(self, text="Register", width=100, height=40, command=self.register)
        self.reg_btn.place(relx=0.5, rely=0.85, anchor=tkinter.CENTER)


    def register(self):
        username = self.reg_username_inputbox.get()
        password = self.reg_password_inputbox.get()
        confirm_password = self.reg_confirm_password_inputbox.get()
        role = self.role_var.get()
        if not username or not password:
            self.set_error("Username and password are required")
            return
        if password != confirm_password:
            self.set_error("Passwords do not match")
            return
        self.set_error("")
        if self.register_callback:
            self.register_callback(username, password, role)

    def set_error(self, message: str):
        self.reg_error_label.configure(text=message)

    def set_credentials(self, username: str = "", password: str = "", confirm_password: str = ""):
        if self.reg_username_inputbox.get() != username:
            self.reg_username_inputbox.delete(0, tkinter.END)
            self.reg_username_inputbox.insert(0, username)
        if self.reg_password_inputbox.get() != password:
            self.reg_password_inputbox.delete(0, tkinter.END)
            self.reg_password_inputbox.insert(0, password)
        if self.reg_confirm_password_inputbox.get() != confirm_password:
            self.reg_confirm_password_inputbox.delete(0, tkinter.END)
            self.reg_confirm_password_inputbox.insert(0, confirm_password)


    def reset(self):
        self.set_credentials()
        self.set_error("")

    def focus(self):
        self.reg_username_inputbox.focus()