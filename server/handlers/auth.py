from protocol.payloads.auth import Credential
from protocol.payloads.common import EmptyPayload


def handle_login(payload: Credential) -> tuple[Credential, bool]:
	# Minimal: accept any credential and echo back with ok=True
	return payload, True


def handle_register(payload: Credential) -> tuple[Credential, bool]:
	# Minimal: accept any registration and echo back
	return payload, True


def handle_logout(payload: EmptyPayload) -> tuple[EmptyPayload, bool]:
	# Minimal: acknowledge logout
	return EmptyPayload(), True
