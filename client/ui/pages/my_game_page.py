import customtkinter
from typing import Callable, Optional


class MyGamePage(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="My Game Page", font=("Arial", 20))
        self.label.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)