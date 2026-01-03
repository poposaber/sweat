import customtkinter
from typing import Callable, Optional

class MyRoomPage(customtkinter.CTkFrame):
    def __init__(self, master, on_join_callback: Optional[Callable[[str], None]] = None):
        super().__init__(master)

        self.label = customtkinter.CTkLabel(self, text="Room Page", font=("Arial", 20))
        self.label.place(relx=0.5, rely=0.3, anchor=customtkinter.CENTER)

        # self.join_button = customtkinter.CTkButton(
        #     self, text="Join Room",
        #     command=lambda: on_join_callback("SampleRoom") if on_join_callback else None
        # )
        # self.join_button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)