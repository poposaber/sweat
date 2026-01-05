import hashlib
import os
import json
from typing import Callable, Optional

from session.session import Session
from protocol.message import Message
from protocol.enums import Action
from protocol.payloads.game import (
    UploadGameInitPayload, UploadGameInitResponsePayload, 
    UploadGameChunkPayload,
    UploadGameFinishPayload,
    FetchStorePayload,
    FetchGameCoverPayload, 
    FetchGameDetailPayload, 
    DownloadGameInitPayload, DownloadGameInitResponsePayload, 
    DownloadGameChunkPayload, DownloadGameChunkResponsePayload, 
    DownloadGameFinishPayload
)
from protocol.payloads.common import EmptyPayload
from client.infra.library_manager import LibraryManager
import zipfile

def upload_game(
    session: Session, 
    name: str, 
    version: str, 
    min_players: int, 
    max_players: int, 
    file_path: str,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Message:
    
    # 1. Calculate SHA256 and size
    try:
        file_size = os.path.getsize(file_path)
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
    except OSError as e:
        return Message.response(Action.UPLOAD_GAME_INIT, None, ok=False, error=f"File error: {e}")

    # 2. Send Init
    init_payload = UploadGameInitPayload(
        name=name,
        version=version,
        min_players=min_players,
        max_players=max_players,
        sha256=file_hash,
        total_size=file_size
    )
    
    req = Message.request(Action.UPLOAD_GAME_INIT, init_payload)
    resp = session.request_response(req)
    
    if not resp.ok:
        return resp
        
    init_resp = resp.payload
    if not isinstance(init_resp, UploadGameInitResponsePayload):
        return Message.response(Action.UPLOAD_GAME_INIT, None, ok=False, error="Invalid server response payload")

    upload_id = init_resp.upload_id
    chunk_size = init_resp.chunk_size
    
    # 3. Send Chunks
    try:
        with open(file_path, "rb") as f:
            chunk_index = 0
            bytes_sent = 0
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                    
                chunk_payload = UploadGameChunkPayload(
                    upload_id=upload_id,
                    chunk_index=chunk_index,
                    data=data
                )
                
                req = Message.request(Action.UPLOAD_GAME_CHUNK, chunk_payload)
                chunk_resp = session.request_response(req)
                
                if not chunk_resp.ok:
                    return chunk_resp
                
                bytes_sent += len(data)
                chunk_index += 1
                
                if progress_callback:
                    progress_callback(bytes_sent, file_size)
    except OSError as e:
        return Message.response(Action.UPLOAD_GAME_CHUNK, None, ok=False, error=f"File read error: {e}")

    # 4. Send Finish
    finish_payload = UploadGameFinishPayload(upload_id=upload_id)
    req = Message.request(Action.UPLOAD_GAME_FINISH, finish_payload)
    return session.request_response(req)

def fetch_my_works(session: Session) -> Message:
    req = Message.request(Action.FETCH_MY_WORKS, EmptyPayload())
    return session.request_response(req)

def fetch_store(session: Session, page: int, page_size: int) -> Message:
    payload = FetchStorePayload(page=page, page_size=page_size)
    req = Message.request(Action.FETCH_STORE, payload)
    return session.request_response(req)

def fetch_game_cover(session: Session, game_name: str) -> Message:
    payload = FetchGameCoverPayload(game_name=game_name)
    req = Message.request(Action.FETCH_GAME_COVER, payload)
    return session.request_response(req)

def fetch_game_detail(session: Session, game_name: str) -> Message:
    payload = FetchGameDetailPayload(game_name=game_name)
    req = Message.request(Action.FETCH_GAME_DETAIL, payload)
    return session.request_response(req)

def download_game(
    session: Session, 
    game_name: str, 
    dest_file_root_path: str,
    library_manager: LibraryManager,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Message:
    # 1. Send Init
    init_payload = DownloadGameInitPayload(game_name=game_name)
    req = Message.request(Action.DOWNLOAD_GAME_INIT, init_payload)
    resp = session.request_response(req)
    
    if not resp.ok:
        return resp
        
    init_resp = resp.payload
    if not isinstance(init_resp, DownloadGameInitResponsePayload):
        return Message.response(Action.DOWNLOAD_GAME_INIT, None, ok=False, error="Invalid server response payload")

    download_id = init_resp.download_id
    chunk_size = init_resp.chunk_size
    total_size = init_resp.total_size
    sha256_expected = init_resp.sha256
    version = init_resp.version
    
    # 2. Receive Chunks
    dest_file_path = os.path.join(dest_file_root_path, f"{download_id}.zip")
    try:
        with open(dest_file_path, "wb") as f:
            bytes_received = 0
            chunk_index = 0
            while bytes_received < total_size:
                chunk_payload = DownloadGameChunkPayload(
                    download_id=download_id,
                    chunk_index=chunk_index
                )
                
                req = Message.request(Action.DOWNLOAD_GAME_CHUNK, chunk_payload)
                chunk_resp = session.request_response(req)
                
                if not chunk_resp.ok:
                    return chunk_resp
                
                chunk_data_payload = chunk_resp.payload
                if not isinstance(chunk_data_payload, DownloadGameChunkResponsePayload):
                    return Message.response(Action.DOWNLOAD_GAME_CHUNK, None, ok=False, error="Invalid server response payload")
                
                f.write(chunk_data_payload.data)
                bytes_received += len(chunk_data_payload.data)
                chunk_index += 1
                
                if progress_callback:
                    progress_callback(bytes_received, total_size)
    except OSError as e:
        return Message.response(Action.DOWNLOAD_GAME_CHUNK, None, ok=False, error=f"File write error: {e}")

    # 3. Send Finish
    finish_payload = DownloadGameFinishPayload(download_id=download_id)
    req = Message.request(Action.DOWNLOAD_GAME_FINISH, finish_payload)

    # 4. Verify SHA256
    sha256_hash = hashlib.sha256()
    try:
        with open(dest_file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        if file_hash != sha256_expected:
            return Message.response(Action.DOWNLOAD_GAME_FINISH, None, ok=False, error="SHA256 mismatch")
    except OSError as e:
        return Message.response(Action.DOWNLOAD_GAME_FINISH, None, ok=False, error=f"File read error: {e}")
    
    # 5. unzip file into ...\<download_id> folder
    extract_folder = os.path.join(dest_file_root_path, download_id)
    os.makedirs(extract_folder, exist_ok=True)
    try:
        with zipfile.ZipFile(dest_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
    except zipfile.BadZipFile as e:
        return Message.response(Action.DOWNLOAD_GAME_FINISH, None, ok=False, error=f"Unzip error: {e}")
    
    # 6. Register game and cleanup
    library_manager.register_game(game_name, version, download_id)

    # Delete the zip file
    try:
        os.remove(dest_file_path)
    except OSError:
        pass
    
    return session.request_response(req)
