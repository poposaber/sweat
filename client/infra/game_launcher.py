import sys
import subprocess
import os
import logging

logger = logging.getLogger(__name__)

class GameLauncher:
    def __init__(self, library_root: str):
        self.library_root = library_root

    def launch_game(self, install_folder_name: str, host: str, port: int, username: str) -> bool:
        """
        Launches a game module from the specified install folder inside the library root.
        
        Args:
            install_folder_name: The name of the folder where the game is installed (e.g., UUID).
            args: Additional command line arguments to pass to the game client.
        
        Returns:
            True if launch process started successfully, False otherwise.
        """
        game_path = os.path.join(self.library_root, install_folder_name)
        
        if not os.path.exists(game_path):
            logger.error(f"Game path does not exist: {game_path}")
            return False

        # Command: python -m client [args...]
        # We need to set the cwd to the game folder so 'client' package is resolvable
        cmd = [sys.executable, "-m", "client", "--host", host, "--port", str(port), "--username", username]
        
        logger.info(f"Launching game from {game_path} with cmd: {cmd}")
        
        try:
            # We use Popen to launch it detached (non-blocking)
            # In a real scenario, we might want to track this process ID
            if os.name == 'nt':
                subprocess.Popen(
                    cmd,
                    cwd=game_path,
                    # We don't pipe stdout/stderr since user said no monitoring needed,
                    # letting it inherit or detach is fine.
                    creationflags=subprocess.CREATE_NEW_CONSOLE # Optional: for Windows to open new window
                )
            else:
                subprocess.Popen(
                    cmd,
                    cwd=game_path,
                    # We don't pipe stdout/stderr since user said no monitoring needed,
                    # letting it inherit or detach is fine.
                    start_new_session=True # Detach from parent terminal
                )
            return True
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            return False
