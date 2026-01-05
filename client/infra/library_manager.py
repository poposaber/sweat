import json
import os
import shutil
from typing import Dict, Optional, TypedDict

class InstalledGame(TypedDict):
    version: str
    install_folder_name: str # will only save the folder path because where games_manifest.json saves will be the root path of games

class LibraryManager:
    MANIFEST_FILENAME = "games_manifest.json"

    def __init__(self, library_root: str):
        self.library_root = library_root
        self.manifest_path = os.path.join(library_root, self.MANIFEST_FILENAME)
        self._ensure_library_exists()

    def _ensure_library_exists(self):
        os.makedirs(self.library_root, exist_ok=True)
        if not os.path.exists(self.manifest_path):
            self._save_manifest({})

    def _load_manifest(self) -> Dict[str, InstalledGame]:
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_manifest(self, manifest: Dict[str, InstalledGame]):
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)

    def get_installed_game(self, game_name: str) -> Optional[InstalledGame]:
        manifest = self._load_manifest()
        return manifest.get(game_name)

    def is_game_installed(self, game_name: str) -> bool:
        return self.get_installed_game(game_name) is not None

    def register_game(self, game_name: str, version: str, install_folder_name: str):
        manifest = self._load_manifest()
        
        # Remove old version if exists
        if game_name in manifest:
            old_info = manifest[game_name]
            old_folder = old_info.get("install_folder_name")
            # If the old path is different from the new path, delete the old folder
            if old_folder and os.path.join(self.library_root, old_folder) != os.path.join(self.library_root, install_folder_name):
                if os.path.exists(os.path.join(self.library_root, old_folder)):
                    try:
                        shutil.rmtree(os.path.join(self.library_root, old_folder))
                    except OSError as e:
                        print(f"Error removing old game version: {e}")

        manifest[game_name] = {
            "version": version,
            "install_folder_name": install_folder_name
        }
        self._save_manifest(manifest)

    def uninstall_game(self, game_name: str):
        manifest = self._load_manifest()
        if game_name in manifest:
            info = manifest[game_name]
            path = info.get("install_path")
            if path and os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except OSError:
                    pass 
            del manifest[game_name]
            self._save_manifest(manifest)

    def get_all_games(self) -> Dict[str, InstalledGame]:
        return self._load_manifest()
