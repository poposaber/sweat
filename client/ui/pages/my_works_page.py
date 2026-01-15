import customtkinter
from tkinter import messagebox, filedialog
from typing import Callable, Optional
from ..components.row_container import RowContainer
from ..components.developed_game_row import DevelopedGameRow

class MyWorksPage(customtkinter.CTkFrame):
    def __init__(self, master, create_template_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)

        # self.label = customtkinter.CTkLabel(self, text="My Works Page", font=("Arial", 20))
        # self.label.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
        self._row_container = RowContainer(self)
        self._row_container.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor=customtkinter.N)

        self._empty_label = customtkinter.CTkLabel(self, text="No games found", font=("Arial", 16))
        self._empty_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        self._create_template_button = customtkinter.CTkButton(self, text="Create New Game Template", command=self.on_create_template_clicked)
        self._create_template_button.place(relx=0.5, rely=0.97, anchor=customtkinter.S)
        self._create_template_callback = create_template_callback

    def add_game_row(self, game_name: str, version: str, min_players: int, max_players: int, command: Optional[Callable[[], None]] = None):
        self._empty_label.place_forget()
        # row = DevelopedGameRow(self._row_container, game_name, version, min_players, max_players, command)
        # self._row_container.add_row(row)
        self._row_container.add_row(DevelopedGameRow, game_name, version, min_players, max_players, command)

    def clear_games(self):
        self._row_container.clear_rows()
        self._empty_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

    def on_create_template_success(self):
        messagebox.showinfo("Success", "Game template created successfully!")

    def on_error(self, error: Exception):
        messagebox.showerror("Error", f"An error occurred: {str(error)}")

    def on_create_template_clicked(self):
        destination_path = filedialog.askdirectory(title="Select Destination Folder")
        if destination_path and self._create_template_callback:
            self._create_template_callback(destination_path, self.on_create_template_success, self.on_error)