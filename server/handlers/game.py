import logging
import os
import hashlib
import zipfile
import shutil
from typing import Tuple, Any

from protocol.payloads.game import (
    UploadGameInitPayload, 
    UploadGameChunkPayload, 
    UploadGameFinishPayload, 
    UploadGameInitResponsePayload,
    FetchMyWorksResponsePayload
)
from protocol.enums import Role
from protocol.payloads.common import EmptyPayload
from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.upload_manager import UploadManager
from session.session import Session
from common.game_version import GameVersion
from pathlib import Path

logger = logging.getLogger(__name__)

GAMES_DIR = "server\\games"
CHUNK_SIZE = 1024 * 1024  # 1MB

def handle_upload_init(
    payload: UploadGameInitPayload, 
    db: Database, 
    upload_manager: UploadManager, 
    session_user_map: SessionUserMap, 
    session: Session
) -> Tuple[UploadGameInitResponsePayload, bool, str]:
    
    addr = session.peer_address
    user_info = session_user_map.get_user_by_session(session)
    if not user_info:
        return UploadGameInitResponsePayload(upload_id="", chunk_size=CHUNK_SIZE), False, "Unauthenticated session"

    role, username = user_info
    if role != Role.DEVELOPER:
        return UploadGameInitResponsePayload(upload_id="", chunk_size=CHUNK_SIZE), False, "Unauthorized action"
    # Validate payload
    if not payload.name or not payload.version:
        return UploadGameInitResponsePayload(upload_id="", chunk_size=CHUNK_SIZE), False, "Missing required fields"
    
    if payload.min_players > payload.max_players:
        return UploadGameInitResponsePayload(upload_id="", chunk_size=CHUNK_SIZE), False, "Min players cannot be greater than max players"
    
    # check if game name already exists
    is_update_text = ""
    existing_game = db.get_game(payload.name)
    if existing_game:
        # treat as update, check developer matches, version greater than existing
        _, existing_developer, existing_version, _, _, _, _ = existing_game
        if existing_developer != username:
            return UploadGameInitResponsePayload(upload_id="", chunk_size=CHUNK_SIZE), False, "Cannot update game owned by another developer"
        
        if GameVersion(payload.version) <= GameVersion(existing_version):
            return UploadGameInitResponsePayload(upload_id="", chunk_size=CHUNK_SIZE), False, "New version must be greater than existing version"
        
        is_update_text = " (update)"

    upload_id = upload_manager.init_upload(
        username=username,
        name=payload.name,
        version=payload.version,
        min_players=payload.min_players,
        max_players=payload.max_players,
        sha256=payload.sha256,
        total_size=payload.total_size
    )
    
    logger.info(f"Upload init{is_update_text}: {payload.name} ({payload.total_size} bytes) by {username}, id={upload_id}")
    
    return UploadGameInitResponsePayload(upload_id=upload_id, chunk_size=CHUNK_SIZE), True, ""

def handle_upload_chunk(
    payload: UploadGameChunkPayload, 
    upload_manager: UploadManager, 
    session: Session
) -> Tuple[EmptyPayload, bool, str]:
    
    # Note: We don't strictly check auth here for performance, relying on upload_id validity
    # But in a real secure system, we should check if session owns the upload_id
    
    success = upload_manager.append_chunk(payload.upload_id, payload.data)
    if not success:
        return EmptyPayload(), False, "Invalid upload ID or write error"
        
    return EmptyPayload(), True, ""

def handle_upload_finish(
    payload: UploadGameFinishPayload, 
    db: Database, 
    upload_manager: UploadManager, 
    session: Session
) -> Tuple[UploadGameFinishPayload, bool, str]:
    
    state = upload_manager.finish_upload(payload.upload_id)
    if not state:
        return payload, False, "Invalid upload ID"

    # Verify size
    if state.current_size != state.total_size:
        upload_manager.cancel_upload(payload.upload_id) # Cleanup
        return payload, False, f"Size mismatch: expected {state.total_size}, got {state.current_size}"

    # Verify hash
    sha256_hash = hashlib.sha256()
    try:
        with open(state.temp_file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        calculated_hash = sha256_hash.hexdigest()
        if calculated_hash != state.sha256:
            os.remove(state.temp_file_path)
            return payload, False, "Hash mismatch"
        
        
            
        # Move to final location
        os.makedirs(GAMES_DIR, exist_ok=True)
        
        # Use upload_id (UUID) for filename to avoid collisions between different games 
        # that might sanitize to the same string.
        # We can keep the original name in the DB for display.
        # We will store two files:
        # 1. {uuid}_client.zip (for players to download)
        # 2. {uuid}_server.zip (for the server to run)
        # The path we store in DB is the base path (without _client.zip or _server.zip)
        
        # Create game directory: server/games/{uuid}
        game_dir = os.path.join(GAMES_DIR, state.upload_id)
        os.makedirs(game_dir, exist_ok=True)
        
        client_zip_path = os.path.join(game_dir, "client.zip")
        server_zip_path = os.path.join(game_dir, "server.zip")
        cover_path = os.path.join(game_dir, "cover.png")
        desc_path = os.path.join(game_dir, "description.txt")
        
        # The path we store in DB is the directory path
        db_file_path = game_dir

        temp_folder = Path(state.temp_file_path).parent
        extract_folder = temp_folder / f"{state.upload_id}"

        client_folder = extract_folder / "client"
        server_folder = extract_folder / "server"
        common_folder = extract_folder / "common"

        try:
            # 1. Extract the uploaded zip
            os.makedirs(extract_folder, exist_ok=True)
            with zipfile.ZipFile(state.temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)

            # 2. Validate Structure
            # Strict check: Only allow 'client', 'server', 'common', 'cover.png', 'description.txt' in root
            root_items = os.listdir(extract_folder)
            allowed_items = {'client', 'server', 'common', 'cover.png', 'description.txt'}
            unknown_items = [item for item in root_items if item not in allowed_items]
            if unknown_items:
                raise ValueError(f"Zip contains forbidden items in root: {unknown_items}. Only 'client/', 'server/', 'common/', 'cover.png', and 'description.txt' are allowed.")

            if not client_folder.exists() or not server_folder.exists():
                raise ValueError("Zip must contain 'client/' and 'server/' folders")
            
            if not (client_folder / "__main__.py").exists():
                 raise ValueError("client/ folder must contain '__main__.py'")
            
            if not (server_folder / "__main__.py").exists():
                 raise ValueError("server/ folder must contain '__main__.py'")
            
            # 3. Move metadata files if they exist
            cover_src = extract_folder / "cover.png"
            if cover_src.exists():
                if cover_src.stat().st_size > 10 * 1024 * 1024:
                    raise ValueError("cover.png is too large. Max size is 10MB.")
                shutil.move(str(cover_src), cover_path)
            
            desc_src = extract_folder / "description.txt"
            if desc_src.exists():
                if desc_src.stat().st_size > 1 * 1024 * 1024:
                    raise ValueError("description.txt is too large. Max size is 1MB.")
                shutil.move(str(desc_src), desc_path)

            # Helper function to create the target zips
            def create_target_zip(target_path: str, source_folder: Path, common_folder: Path):
                with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as z:
                    # A. Add source folder contents to the ROOT of the zip
                    #    e.g. client/main.py -> client/main.py (Structure Preserved)
                    for root, _, files in os.walk(source_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, extract_folder) # preserve structure under source_folder to make sure game works
                            z.write(file_path, arcname)
                    
                    # B. Add common folder to 'common/' in the zip
                    #    e.g. common/consts.py -> common/consts.py
                    if common_folder.exists():
                        for root, _, files in os.walk(common_folder):
                            for file in files:
                                file_path = os.path.join(root, file)
                                # We want the arcname to start with 'common/'
                                # os.path.relpath(..., extract_dir) gives 'common/...'
                                arcname = os.path.relpath(file_path, extract_folder)
                                z.write(file_path, arcname)
            # 4. Create client zip
            create_target_zip(client_zip_path, client_folder, common_folder)
            # 5. Create server zip
            create_target_zip(server_zip_path, server_folder, common_folder)

        except Exception as e:
            logger.error(f"Error processing uploaded zip for {state.game_name}: {e}")
            # Cleanup created directory on error
            if os.path.exists(game_dir):
                shutil.rmtree(game_dir, ignore_errors=True)
            return payload, False, f"Invalid zip structure: {e}"
        finally:
            # Cleanup extracted temp folder
            shutil.rmtree(extract_folder, ignore_errors=True)
            # Remove the original uploaded zip
            if os.path.exists(state.temp_file_path):
                os.remove(state.temp_file_path)

        
        # Move file (overwrite if exists)
        # if os.path.exists(final_path):
        #     os.remove(final_path)
        # os.rename(state.temp_file_path, final_path)
        
        # Update DB
        # get game first, if exists, update; else create new

        existing_game = db.get_game(state.game_name)
        if existing_game:
            # existing_game: (name, developer, version, min_players, max_players, sha256, file_path)
            existing_developer = existing_game[1]
            existing_version_str = existing_game[2]
            old_file_path = existing_game[6]

            if existing_developer != state.username:
                shutil.rmtree(game_dir, ignore_errors=True)
                return payload, False, "Permission denied: You are not the developer of this game"

            try:
                new_ver = GameVersion(state.version)
                old_ver = GameVersion(existing_version_str)
                if new_ver <= old_ver:
                    shutil.rmtree(game_dir, ignore_errors=True)
                    return payload, False, f"Version must be greater than current version {existing_version_str}"
            except ValueError as e:
                shutil.rmtree(game_dir, ignore_errors=True)
                return payload, False, f"Invalid version format: {e}"
            
            # remove old file/directory
            if os.path.exists(old_file_path):
                if os.path.isdir(old_file_path):
                    shutil.rmtree(old_file_path, ignore_errors=True)
                # else:
                #     # It might be the old zip files (legacy)
                #     if os.path.exists(old_file_path + "_client.zip"):
                #         os.remove(old_file_path + "_client.zip")
                #     if os.path.exists(old_file_path + "_server.zip"):
                #         os.remove(old_file_path + "_server.zip")

            success = db.set_game(
                name=state.game_name,
                version=state.version,
                min_players=state.min_players,
                max_players=state.max_players,
                sha256=state.sha256,
                file_path=db_file_path
            )
        else:
            success = db.create_game(
                name=state.game_name,
                developer=state.username,
                version=state.version,
                min_players=state.min_players,
                max_players=state.max_players,
                sha256=state.sha256,
                file_path=db_file_path
            )
            
        if not success:
            shutil.rmtree(game_dir, ignore_errors=True)
            return payload, False, "Database error"

        logger.info(f"Upload finished: {state.game_name} v{state.version} by {state.username}")
        return payload, True, ""
        
    except Exception as e:
        logger.error(f"Error finalizing upload {payload.upload_id}: {e}")
        if os.path.exists(state.temp_file_path):
            os.remove(state.temp_file_path)
        
        # Cleanup game dir if it was created
        game_dir = os.path.join(GAMES_DIR, state.upload_id)
        if os.path.exists(game_dir):
            shutil.rmtree(game_dir, ignore_errors=True)
            
        return payload, False, "Internal server error"

def handle_fetch_my_works(
    payload: EmptyPayload, 
    db: Database,
    session_user_map: SessionUserMap, 
    session: Session
) -> Tuple[FetchMyWorksResponsePayload, bool, str]:
    user_info = session_user_map.get_user_by_session(session)
    if not user_info:
        return FetchMyWorksResponsePayload(works=[]), False, "Unauthenticated session"
    
    role, username = user_info
    if not username or role != Role.DEVELOPER:
        return FetchMyWorksResponsePayload(works=[]), False, "Unauthorized"
    games = db.get_games_by_developer(username)
    # reduce to (name, version, min_players, max_players)
    games = [(name, version, min_players, max_players) for (name, _, version, min_players, max_players, _, _) in games]
    return FetchMyWorksResponsePayload(works=games), True, ""