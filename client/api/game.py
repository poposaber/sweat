import hashlib
import os
from typing import Callable, Optional

from session.session import Session
from protocol.message import Message
from protocol.enums import Action
from protocol.payloads.game import (
    UploadGameInitPayload,
    UploadGameChunkPayload,
    UploadGameFinishPayload,
    UploadGameInitResponsePayload, 
    FetchStorePayload,
    FetchGameCoverPayload
)
from protocol.payloads.common import EmptyPayload

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
