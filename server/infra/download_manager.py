import uuid
import os
import math
import logging
import time
from typing import Optional
import threading
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class DownloadState:
    total_size: int
    chunk_size: int
    file_path: str

class DownloadManager:
    def __init__(self):
        self._downloads: dict[str, DownloadState] = {}
        self._lock = threading.Lock()

    def init_download(self, chunk_size: int, file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            logger.error("File %s does not exist for download", file_path)
            return None

        download_id = str(uuid.uuid4())
        total_size = os.path.getsize(file_path)
        
        state = DownloadState(
            file_path=file_path,
            chunk_size=chunk_size,
            total_size=total_size
        )
        
        with self._lock:
            self._downloads[download_id] = state
            
        return download_id
    
    def get_chunk(self, download_id: str, chunk_index: int) -> Optional[bytes]:
        with self._lock:
            state = self._downloads.get(download_id)
            if not state:
                logger.error("Download ID %s not found", download_id)
                return None
            
        offset = chunk_index * state.chunk_size
        if offset >= state.total_size:
            logger.info("Chunk index %d out of range for download ID %s", chunk_index, download_id)
            return None
        read_size = min(state.chunk_size, state.total_size - offset)
        try:
            with open(state.file_path, "rb") as f:
                f.seek(offset)
                data = f.read(read_size)
                return data
        except Exception as e:
            logger.error("Error reading chunk %d for download ID %s: %s", chunk_index, download_id, e)
            return None
        
    def get_total_chunks(self, download_id: str) -> Optional[int]:
        with self._lock:
            state = self._downloads.get(download_id)
            if not state:
                logger.error("Download ID %s not found", download_id)
                return None
        total_chunks = math.ceil(state.total_size / state.chunk_size)
        return total_chunks
    
    def get_total_size(self, download_id: str) -> Optional[int]:
        with self._lock:
            state = self._downloads.get(download_id)
            if not state:
                logger.error("Download ID %s not found", download_id)
                return None
        return state.total_size
    
    def get_sha256(self, download_id: str) -> Optional[str]:
        with self._lock:
            state = self._downloads.get(download_id)
            if not state:
                logger.error("Download ID %s not found", download_id)
                return None
        try:
            sha256_hash = hashlib.sha256()
            with open(state.file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error("Error calculating SHA256 for download ID %s: %s", download_id, e)
            return None
    
    def finish_download(self, download_id: str) -> bool:
        with self._lock:
            if download_id in self._downloads:
                del self._downloads[download_id]
                return True
            else:
                logger.error("Download ID %s not found for finishing", download_id)
                return False

    