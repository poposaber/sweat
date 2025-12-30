import customtkinter
from typing import Callable, Optional
import tkinter
from tkinter import simpledialog, messagebox
from ..components.file_browser import FileBrowser
from ..components.version_input import VersionInput
from ..components.min_max_player_input import MinMaxPlayerInput

class UploadPage(customtkinter.CTkFrame):
    def __init__(self, master, on_upload_callback: Optional[Callable[[str, str, int, int, str], None]] = None):
        super().__init__(master)
        self.on_upload_callback = on_upload_callback

        self.label = customtkinter.CTkLabel(self, text="Upload Page", font=("Arial", 20))
        self.label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

        self.name_label = customtkinter.CTkLabel(self, text="Game Name")
        self.name_label.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
        self.name_inputbox = customtkinter.CTkEntry(self, width=300, height=30)
        self.name_inputbox.place(relx=0.5, rely=0.25, anchor=tkinter.CENTER)

        self.version_label = customtkinter.CTkLabel(self, text="Version (Major.Minor.Patch)")
        self.version_label.place(relx=0.5, rely=0.35, anchor=tkinter.CENTER)
        self.version_inputbox = VersionInput(self, width=300, height=30)
        self.version_inputbox.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)

        self.players_label = customtkinter.CTkLabel(self, text="Player Count")
        self.players_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.min_max_player_input = MinMaxPlayerInput(self, width=300, height=30)
        self.min_max_player_input.place(relx=0.5, rely=0.55, anchor=tkinter.CENTER)

        self.file_label = customtkinter.CTkLabel(self, text="Game File (.zip)")
        self.file_label.place(relx=0.5, rely=0.65, anchor=tkinter.CENTER)
        self.file_browser = FileBrowser(self, width=400, height=30, 
                                        filetypes=[("ZIP Files", "*.zip")],
                                        on_browse_done=self.on_file_selected)
        self.file_browser.place(relx=0.5, rely=0.7, anchor=tkinter.CENTER)
        
        self._upload_btn = customtkinter.CTkButton(self, text="Upload", command=self.upload_file)
        self._upload_btn.place(relx=0.5, rely=0.85, anchor=tkinter.CENTER)
    def on_file_selected(self, path: str):
        print(f"File selected: {path}")

    def upload_file(self):
        game_name = self.name_inputbox.get()
        version = self.version_inputbox.get_version()
        min_players, max_players = self.min_max_player_input.get_min_max()
        file_path = self.file_browser.entry.get()

        if not game_name:
            messagebox.showerror("Error", "Please enter a game name.")
            return
        if not self.version_inputbox.is_valid():
            messagebox.showerror("Error", "Please enter a valid version number.")
            return
        if not min_players or not max_players:
            messagebox.showerror("Error", "Please enter valid min and max player counts.")
            return
        
        if min_players > max_players:
            messagebox.showerror("Error", "Min players cannot be greater than max players.")
            return
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload.")
            return

        if self.on_upload_callback:
            self.on_upload_callback(game_name, version, min_players, max_players, file_path)

        