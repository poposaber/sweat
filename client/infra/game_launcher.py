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
        abs_game_path = os.path.abspath(game_path)
        
        if not os.path.exists(abs_game_path):
            logger.error(f"Game path does not exist: {abs_game_path}")
            return False

        # Determine python executable and environment
        env = os.environ.copy()
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            # If frozen (PyInstaller), look for the bundled python folder relative to the exe
            base_dir = os.path.dirname(sys.executable)
            python_executable = os.path.join(base_dir, "python", "python.exe")
        else:
            python_executable = sys.executable

        # Construct safe command that sets sys.path explicitly at runtime
        # This bypasses limitations of Embeddable Python not respecting PYTHONPATH
        bootstrap_script = (
            "import sys; "
            "import runpy; "
            f"sys.path.insert(0, {repr(abs_game_path)}); "
        )
        
        if is_frozen:
            # Add base_dir (dist root) to path so shared modules (protocol, common) are found
            bootstrap_script += f"sys.path.append({repr(base_dir)}); "
            
        bootstrap_script += "runpy.run_module('client', run_name='__main__', alter_sys=True)"

        # Command: python -c "..." [args...]
        cmd = [python_executable, "-c", bootstrap_script, "--host", host, "--port", str(port), "--username", username]
        
        logger.info(f"Launching game from {abs_game_path} with cmd: {cmd}")
        
        try:
            # We use Popen to launch it detached (non-blocking)
            # In a real scenario, we might want to track this process ID
            
            # Setup logging for the subprocess
            # log_path = os.path.join(abs_game_path, "launch_log.txt")
            # with open(log_path, "w") as log_file:
            #     # Basic diagnostics in log file
            #     log_file.write(f"Launching game...\n")
            #     log_file.write(f"CWD: {abs_game_path}\n")
            #     log_file.write(f"CMD (Log): {cmd}\n")
            #     log_file.write("Redirecting output to console for gameplay.\n")
            #     log_file.flush()
                
            if os.name == 'nt':
                subprocess.Popen(
                    cmd,
                    cwd=abs_game_path,
                    env=env,
                    # stdout=log_file, # Removed strict redirection to let user interact in console
                    # stderr=log_file,
                    creationflags=subprocess.CREATE_NEW_CONSOLE 
                )
            else:
                subprocess.Popen(
                    cmd,
                    cwd=abs_game_path,
                    env=env,
                    # stdout=log_file,
                    # stderr=log_file,
                    start_new_session=True # Detach from parent terminal
                )
            return True
        except Exception as e:
            logger.error(f"Failed to launch game: {e}")
            return False
