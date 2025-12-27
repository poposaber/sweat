from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload
from server.infra.database import Database
from protocol.enums import Role


def handle_login(payload: Credential, db: Database) -> tuple[Credential, bool, str | None]:
	if payload.role == Role.DEVELOPER.value:
		user = db.get_developer(payload.username)
	else:
		user = db.get_player(payload.username)

	if not user:
		return payload, False, "User not found"
	
	stored_username, stored_password = user
	if stored_password != payload.password:
		return payload, False, "Incorrect password"
	
	return payload, True, None


def handle_register(payload: Credential, db: Database) -> tuple[Credential, bool, str | None]:
	if payload.role == Role.DEVELOPER.value:
		success = db.create_developer(payload.username, payload.password)
	else:
		success = db.create_player(payload.username, payload.password)

	if not success:
		return payload, False, "Username already exists"
	return payload, True, None


def handle_logout(payload: EmptyPayload) -> tuple[EmptyPayload, bool, str | None]:
	# Minimal: acknowledge logout
	return EmptyPayload(), True, None
