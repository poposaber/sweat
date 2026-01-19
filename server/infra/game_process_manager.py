import sys
import socket
import subprocess
import threading
import logging
import os
import shutil
import uuid
import zipfile
from typing import Dict, Optional, Tuple, Callable

logger = logging.getLogger(__name__)

class GameProcessManager:
    def __init__(self, base_run_dir: str = "server/running_games"):
        self._input_base_run_dir = base_run_dir
        self._run_dir = os.path.abspath(base_run_dir)
        self._running_processes: Dict[str, subprocess.Popen] = {} # room_id -> Popen
        self._port_map: Dict[str, int] = {} # room_id -> port
        self._starting_rooms: set[str] = set() # room_id
        self._lock = threading.Lock()
        
        # Ensure run dir exists
        if os.path.exists(self._run_dir):
            # Cleanup previous runs? Maybe dangerous if server restarted but games persist?
            # For now, let's assume we can clean up
            pass
        else:
            os.makedirs(self._run_dir, exist_ok=True)

    def _find_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def start_game_server(self, room_id: str, game_server_zip_path: str, on_game_end: Optional[Callable[[str], None]] = None) -> Tuple[bool, int, str]:
        """
        Starts a game server for a specific room.
        Returns: (success, port, error_message)
        """
        with self._lock:
            if room_id in self._starting_rooms:
                logger.warning(f"Start game blocked: Room {room_id} is already starting")
                return True, 0, "" # Threat as success but do nothing (idempotent)
            
            if room_id in self._running_processes:
                # Check if still running
                proc = self._running_processes[room_id]
                if proc.poll() is None:
                    logger.warning(f"Start game blocked: Room {room_id} has running process")
                    return True, 0, "" # Threat as success (already running)
                else:
                    # Cleanup dead process
                    logger.info(f"Cleaning up dead process for room {room_id} before restart")
                    self.stop_game_server(room_id)
            
            self._starting_rooms.add(room_id)

        try:
            # 1. Find free port
            port = self._find_free_port()
            logger.info(f"Allocated port {port} for room {room_id}")

            # 2. Prepare runtime directory
            room_run_dir = os.path.join(self._run_dir, room_id)
            if os.path.exists(room_run_dir):
                shutil.rmtree(room_run_dir)
            os.makedirs(room_run_dir, exist_ok=True)

            # 3. Unzip server files
            if not os.path.exists(game_server_zip_path):
                return False, 0, f"Game server file not found: {game_server_zip_path}"

            with zipfile.ZipFile(game_server_zip_path, 'r') as zip_ref:
                zip_ref.extractall(room_run_dir)

            # 4. Determine executable
            cmd = []
            
            if os.path.exists(os.path.join(room_run_dir, "server/__main__.py")):
                # Use -u for unbuffered output so logs appear immediately
                cmd = [sys.executable, "-u", "-m", "server", "--port", str(port)] 
            else:
                return False, 0, "No executable found in game server package (__main__.py)"

            logger.info(f"Starting game server for room {room_id}: {cmd}")

            # Prepare environment: Add project root to PYTHONPATH so shared modules (like protocol) are found
            # server/infra/game_process_manager.py -> server/infra -> server -> root (2 levels up)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            env = os.environ.copy()
            env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
            
            # 5. Start process
            # Use PIPE to capture stdout and check for READY
            proc = subprocess.Popen(
                cmd, 
                cwd=room_run_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8', # Force UTF-8 for consistency
                errors='replace', # Replace invalid characters instead of crashing
                bufsize=1
            )

            # 6. Monitor output for READY
            log_path = os.path.join(room_run_dir, "server.log")
            ready_event = threading.Event()

            def _monitor_logs():
                try:
                    # Use utf-8 for log file
                    with open(log_path, "w", encoding='utf-8') as f:
                        assert proc.stdout is not None
                        for line in iter(proc.stdout.readline, ''):
                            f.write(line)
                            f.flush()
                            if "READY" in line and not ready_event.is_set():
                                ready_event.set()
                            
                            if "GAME_END" in line:
                                logger.info(f"Game end detected for room {room_id}")
                                self.stop_game_server(room_id)
                                if on_game_end:
                                    try:
                                        # For simplicity, we just call the callback with no payload
                                        # Parse payload if needed, now just trigger callback
                                        # Example: GAME_END {"winner": "alice"}
                                        # payload = line.split("GAME_END", 1)[1].strip()
                                        on_game_end(room_id)
                                    except Exception as e:
                                        logger.error(f"Error executing on_game_end callback: {e}")

                except Exception as e:
                    logger.error(f"Error monitoring logs for room {room_id}: {e}")

            t = threading.Thread(target=_monitor_logs, daemon=True)
            t.start()

            # Wait for READY signal
            if not ready_event.wait(timeout=10.0):
                logger.error(f"Timeout waiting for READY signal for room {room_id}")
                proc.terminate()
                return False, 0, "Timeout waiting for game server readiness"
            
            # Check if process died immediately
            if proc.poll() is not None:
                return False, 0, f"Game server exited immediately with code {proc.returncode}"
            
            with self._lock:
                self._running_processes[room_id] = proc
                self._port_map[room_id] = port
            
            return True, port, ""

        except Exception as e:
            logger.error(f"Failed to start game server for room {room_id}: {e}")
            return False, 0, str(e)
        finally:
             with self._lock:
                 self._starting_rooms.discard(room_id)

    def stop_game_server(self, room_id: str):
        with self._lock:
            if room_id in self._running_processes:
                proc = self._running_processes[room_id]
                if proc.poll() is None:
                    logger.info(f"Stopping game server for room {room_id}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
            
            del self._running_processes[room_id]
            if room_id in self._port_map:
                del self._port_map[room_id]
            
            # Cleanup files? Maybe keep logs for debugging.
            # room_run_dir = os.path.join(self._run_dir, room_id)
            # if os.path.exists(room_run_dir):
            #     shutil.rmtree(room_run_dir)

    def get_server_info(self, room_id: str) -> Optional[tuple[int, subprocess.Popen]]:
        if room_id not in self._running_processes:
            return None
        
        port = self._port_map.get(room_id)
        if port is None:
            return None
        
        proc = self._running_processes[room_id]
        return port, proc
        # if room_id in self._running_processes:
        #     return self._port_map.get(room_id), self._running_processes[room_id]
        # return None

    def clean_cache(self, room_id: str):
        room_run_dir = os.path.join(self._run_dir, room_id)
        if os.path.exists(room_run_dir):
            shutil.rmtree(room_run_dir)
