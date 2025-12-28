from protocol.enums import Action, MessageType
from protocol.message import Message
from server.handlers import auth as auth_handlers
from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from session.session import Session


class Dispatcher:
	def __init__(self, db: Database, session_user_map: SessionUserMap):
		self._db = db
		self._session_user_map = session_user_map

	def dispatch(self, message: Message, session: Session) -> Message:
		# Only handle requests; for non-request, echo payload and mark failed
		assert message.action is not None
		if message.type != MessageType.REQUEST:
			return Message.response(
				message.action,
				message.payload,
				msg_id=message.msg_id,
				ok=False,
			)

		if message.action == Action.LOGIN:
			payload, ok, error = auth_handlers.handle_login(message.payload, self._db, self._session_user_map, session)
		elif message.action == Action.REGISTER:
			payload, ok, error = auth_handlers.handle_register(message.payload, self._db, session)
		elif message.action == Action.LOGOUT:
			payload, ok, error = auth_handlers.handle_logout(message.payload, self._session_user_map, session)
		else:
			# Unknown action: echo payload, mark failed
			payload, ok, error = message.payload, False, "Unknown action"

		return Message.response(
			message.action,
			payload,
			msg_id=message.msg_id,
			ok=ok,
			error=error,
		)
