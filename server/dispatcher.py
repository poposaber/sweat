from protocol.enums import Action, MessageType
from protocol.message import Message
from server.handlers import auth as auth_handlers


class Dispatcher:
	def dispatch(self, message: Message) -> Message:
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
			payload, ok = auth_handlers.handle_login(message.payload)
		elif message.action == Action.REGISTER:
			payload, ok = auth_handlers.handle_register(message.payload)
		elif message.action == Action.LOGOUT:
			payload, ok = auth_handlers.handle_logout(message.payload)
		else:
			# Unknown action: echo payload, mark failed
			payload, ok = message.payload, False

		return Message.response(
			message.action,
			payload,
			msg_id=message.msg_id,
			ok=ok,
		)
