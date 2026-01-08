import customtkinter
from typing import Callable, Optional

class PlayersSlide(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Players Slide", font=("Arial", 20))
        self.label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)