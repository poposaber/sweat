import customtkinter
from typing import Callable, Optional
import tkinter
from tkinter import messagebox
from ..components.file_browser import FileBrowser
from ..components.version_input import VersionInput
from ..components.min_max_player_input import MinMaxPlayerInput
from ..components.clickable_label import ClickableLabel
import zipfile

class UploadPage(customtkinter.CTkFrame):
    def __init__(self, master, on_upload_callback: Optional[Callable[[str, str, int, int, str], None]] = None):
        super().__init__(master)
        self.on_upload_callback = on_upload_callback

        self.label = customtkinter.CTkLabel(self, text="Upload Page", font=("Arial", 20))
        self.label.place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

        self.rule_label = ClickableLabel(self, text="Upload Rules", font=("Arial", 12, "underline"), command=self.show_upload_rules)
        self.rule_label.place(relx=0.95, rely=0.1, anchor=tkinter.E)

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
        
        if not file_path.lower().endswith(".zip"):
            messagebox.showerror("Error", "Only .zip files are allowed for upload.")
            return
        
        # open the file. We check:
        # 1. there is a client/__main__.py
        # 2. there is a server/__main__.py
        # 3. no other files than cover.png and description.txt and common/ folder
        # 4. optional: cover.png (<=10MB), description.txt (<=1MB)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            namelist = zip_ref.namelist()
            if not any(name.startswith("client/") and name.endswith("__main__.py") for name in namelist):
                messagebox.showerror("Error", "The zip file must contain client/__main__.py")
                return
            if not any(name.startswith("server/") and name.endswith("__main__.py") for name in namelist):
                messagebox.showerror("Error", "The zip file must contain server/__main__.py")
                return
            
            # Check for invalid files
            allowed_files = {"cover.png", "description.txt"}
            allowed_dirs = {"client/", "server/", "common/"}
            for name in namelist:
                if not any(name.startswith(dir_name) for dir_name in allowed_dirs) and name not in allowed_files:
                    messagebox.showerror("Error", f"Invalid file or folder in zip: {name}")
                    return
                # Check size of optional files
                if name == "cover.png":
                    info = zip_ref.getinfo(name)
                    if info.file_size > 10 * 1024 * 1024:
                        messagebox.showerror("Error", "cover.png is too large. Max size is 10MB.")
                        return
                if name == "description.txt":
                    info = zip_ref.getinfo(name)
                    if info.file_size > 1 * 1024 * 1024:
                        messagebox.showerror("Error", "description.txt is too large. Max size is 1MB.")
                        return

        if self.on_upload_callback:
            self.on_upload_callback(game_name, version, min_players, max_players, file_path)

    def show_upload_rules(self):
        rules = (
            "Upload Rules:\n"
            "- Game name must be unique.\n"
            "- Version must follow the Major.Minor.Patch format.\n"
            "- Min players must be less than or equal to max players.\n"
            "- Only .zip files are allowed for upload. You can only upload one file at a time.\n"
            "- The structure of .zip file: \n"
            "   xxx.zip\n"
            "       client\n"
            "           __main__.py\n"
            "       server\n"
            "           __main__.py\n"
            "       common (optional)\n"
            "       cover.png (optional, max size 10MB)\n"
            "       description.txt (optional, max size 1MB)\n"
            "- No other files or folders are allowed in the root of the zip.\n"
            "- For updating, upload a new version with the same game name."
        )
        messagebox.showinfo("Upload Rules", rules)

        