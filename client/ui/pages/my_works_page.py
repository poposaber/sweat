import customtkinter
from tkinter import messagebox, filedialog
from typing import Callable, Optional
from ..components.row_container import RowContainer
from ..components.developed_game_row import DevelopedGameRow
from ..components.developed_game_row_container import DevelopedGameRowContainer

class MyWorksPage(customtkinter.CTkFrame):
    def __init__(self, master, 
                 fetch_my_works_callback: Optional[Callable[[Callable[[list[tuple[str, str, int, int]]], None], Callable[[Exception], None]], None]] = None,
                 create_template_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None]], None]] = None, 
                 remove_game_callback: Optional[Callable[[str, Callable[[], None], Callable[[Exception], None]], None]] = None):
        super().__init__(master)

        # self.label = customtkinter.CTkLabel(self, text="My Works Page", font=("Arial", 20))
        # self.label.place(relx=0.5, rely=0.3, anchor=tkinter.CENTER)
        self._row_container = DevelopedGameRowContainer(self)
        self._row_container.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor=customtkinter.N)

        self._empty_label = customtkinter.CTkLabel(self, text="No games found", font=("Arial", 16))
        self._empty_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        self._create_template_button = customtkinter.CTkButton(self, text="Create New Game Template", command=self.on_create_template_clicked)
        self._create_template_button.place(relx=0.5, rely=0.97, anchor=customtkinter.S)
        self._create_template_callback = create_template_callback
        self._remove_game_callback = remove_game_callback
        self._fetch_my_works_callback = fetch_my_works_callback
        
    def add_game_row(self, game_name: str, version: str, min_players: int, max_players: int):
        self._empty_label.place_forget()
        # row = DevelopedGameRow(self._row_container, game_name, version, min_players, max_players, command)
        # self._row_container.add_row(row)
        def remove_command():
            if self._remove_game_callback:
                if messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove {game_name}?"):
                    self._remove_game_callback(
                        game_name,
                        self.on_remove_game_success,
                        self.on_error
                    )
        self._row_container.add_game_row(game_name, version, min_players, max_players, remove_command)

    def refresh(self):
        if self._fetch_my_works_callback:
            self._fetch_my_works_callback(
                self.on_fetch_my_works_success,
                self.on_error
            )

    def clear_games(self):
        self._row_container.clear_game_rows()
        self._empty_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

    def on_create_template_success(self):
        messagebox.showinfo("Success", "Game template created successfully!")

    def on_remove_game_success(self):
        messagebox.showinfo("Success", "Game removed successfully!")
        self.refresh()

    def on_fetch_my_works_success(self, works: list[tuple[str, str, int, int]]):
        self.clear_games()
        if not works:
            return
        for game_name, version, min_players, max_players in works:
            self.add_game_row(game_name, version, min_players, max_players)

    def on_error(self, error: Exception):
        messagebox.showerror("Error", f"An error occurred: {str(error)}")

    def on_create_template_clicked(self):
        destination_path = filedialog.askdirectory(title="Select Destination Folder")
        if destination_path and self._create_template_callback:
            self._create_template_callback(destination_path, self.on_create_template_success, self.on_error)