import uuid
import os
import time
import threading
from dataclasses import dataclass
from typing import Optional

@dataclass
class UploadState:
    upload_id: str
    username: str
    game_name: str
    version: str
    min_players: int
    max_players: int
    sha256: str
    total_size: int
    current_size: int
    temp_file_path: str
    last_activity: float

class UploadManager:
    def __init__(self, temp_dir: str = "server\\temp_uploads"):
        self._temp_dir = temp_dir
        self._uploads: dict[str, UploadState] = {}
        self._lock = threading.Lock()
        
        os.makedirs(self._temp_dir, exist_ok=True)

    def init_upload(self, username: str, name: str, version: str, min_players: int, max_players: int, sha256: str, total_size: int) -> str:
        upload_id = str(uuid.uuid4())
        temp_file_path = os.path.join(self._temp_dir, f"{upload_id}.part")
        
        state = UploadState(
            upload_id=upload_id,
            username=username,
            game_name=name,
            version=version,
            min_players=min_players,
            max_players=max_players,
            sha256=sha256,
            total_size=total_size,
            current_size=0,
            temp_file_path=temp_file_path,
            last_activity=time.time()
        )
        
        with self._lock:
            self._uploads[upload_id] = state
            
        # Create empty file
        with open(temp_file_path, "wb") as f:
            pass
            
        return upload_id

    def append_chunk(self, upload_id: str, data: bytes) -> bool:
        with self._lock:
            state = self._uploads.get(upload_id)
            if not state:
                return False
            
            state.last_activity = time.time()
            
        try:
            with open(state.temp_file_path, "ab") as f:
                f.write(data)
            
            with self._lock:
                state.current_size += len(data)
                
            return True
        except Exception:
            return False

    def get_upload(self, upload_id: str) -> Optional[UploadState]:
        with self._lock:
            return self._uploads.get(upload_id)

    def finish_upload(self, upload_id: str) -> Optional[UploadState]:
        with self._lock:
            return self._uploads.pop(upload_id, None)

    def cancel_upload(self, upload_id: str):
        with self._lock:
            state = self._uploads.pop(upload_id, None)
        
        if state and os.path.exists(state.temp_file_path):
            try:
                os.remove(state.temp_file_path)
            except OSError:
                pass
