import logging
from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload
from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.room_manager import RoomManager
from session.session import Session
from protocol.enums import Role

logger = logging.getLogger(__name__)


def handle_login(payload: Credential, db: Database, session_user_map: SessionUserMap, session: Session) -> tuple[Credential, bool, str | None]:
	addr = session.peer_address
	logger.info(f"Login attempt: user={payload.username}, role={payload.role}, addr={addr}")

	try:
		role = Role(payload.role)
	except ValueError:
		logger.warning(f"Login failed: Invalid role - {payload.role}")
		return payload, False, "Invalid role"

	if role == Role.DEVELOPER:
		user = db.get_developer(payload.username)
	else:
		user = db.get_player(payload.username)

	if not user:
		logger.warning(f"Login failed: User not found - {payload.username}")
		return payload, False, "User not found"
	
	stored_username, stored_password = user
	if stored_password != payload.password:
		logger.warning(f"Login failed: Incorrect password - {payload.username}")
		return payload, False, "Incorrect password"
	
	# Check if already logged in
	if session_user_map.get_session_by_user(role, payload.username):
		logger.warning(f"Login failed: User already logged in - {payload.username}")
		return payload, False, "User already logged in"
	
	# Login success: update session map
	session_user_map.move_session_to_user(session, role, payload.username)

	logger.info(f"Login success: {payload.username} as {payload.role}")
	return payload, True, None


def handle_register(payload: Credential, db: Database, session: Session) -> tuple[Credential, bool, str | None]:
	addr = session.peer_address
	logger.info(f"Register attempt: user={payload.username}, role={payload.role}, addr={addr}")

	if payload.role == Role.DEVELOPER.value:
		success = db.create_developer(payload.username, payload.password)
	else:
		success = db.create_player(payload.username, payload.password)

	if not success:
		logger.warning(f"Register failed: Username already exists - {payload.username}")
		return payload, False, "Username already exists"
	
	logger.info(f"Register success: {payload.username} as {payload.role}")
	return payload, True, None


def handle_logout(payload: EmptyPayload, room_manager: RoomManager, session_user_map: SessionUserMap, session: Session) -> tuple[EmptyPayload, bool, str | None]:
	addr = session.peer_address
	logger.info(f"Logout attempt: addr={addr}")

	user_info = session_user_map.get_user_by_session(session)
	if user_info:
		role, username = user_info
		if role == Role.PLAYER:
			room_id = room_manager.get_room_id_by_player(username)
			if room_id:
				room_manager.remove_player_from_room(room_id, username)
				logger.info(f"User {username} removed from room {room_id} on logout")

		session_user_map.move_session_back(session)
		logger.info(f"Logout success: {username} ({role.value}) session moved back")
	else:
		logger.info(f"Logout: Session was not logged in or already logged out")
	
	return EmptyPayload(), True, None
