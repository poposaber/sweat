from protocol.enums import Action, MessageType
from protocol.message import Message
from server.handlers import auth as auth_handlers
from server.handlers import game as game_handlers
from server.handlers import room as room_handlers
from server.infra.database import Database
from server.infra.session_user_map import SessionUserMap
from server.infra.upload_manager import UploadManager
from server.infra.download_manager import DownloadManager
from server.infra.room_manager import RoomManager
from session.session import Session


class Dispatcher:
	def __init__(self, db: Database, session_user_map: SessionUserMap, room_manager: RoomManager):
		self._db = db
		self._session_user_map = session_user_map
		self._upload_manager = UploadManager()
		self._download_manager = DownloadManager()
		self._room_manager = room_manager

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
		
		match message.action:
			case Action.LOGIN:
				payload, ok, error = auth_handlers.handle_login(message.payload, self._db, self._session_user_map, session)
			case Action.REGISTER:
				payload, ok, error = auth_handlers.handle_register(message.payload, self._db, session)
			case Action.LOGOUT:
				payload, ok, error = auth_handlers.handle_logout(message.payload, self._room_manager, self._session_user_map, session)
			case Action.UPLOAD_GAME_INIT:
				payload, ok, error = game_handlers.handle_upload_init(message.payload, self._db, self._upload_manager, self._session_user_map, session)
			case Action.UPLOAD_GAME_CHUNK:
				payload, ok, error = game_handlers.handle_upload_chunk(message.payload, self._upload_manager, session)
			case Action.UPLOAD_GAME_FINISH:
				payload, ok, error = game_handlers.handle_upload_finish(message.payload, self._db, self._upload_manager, session)
			case Action.FETCH_MY_WORKS:
				payload, ok, error = game_handlers.handle_fetch_my_works(message.payload, self._db, self._session_user_map, session)
			case Action.FETCH_STORE:
				payload, ok, error = game_handlers.handle_fetch_store(message.payload, self._db, self._session_user_map, session)
			case Action.FETCH_GAME_COVER:
				payload, ok, error = game_handlers.handle_fetch_game_cover(message.payload, self._db, self._session_user_map, session)
			case Action.FETCH_GAME_DETAIL:
				payload, ok, error = game_handlers.handle_fetch_game_detail(message.payload, self._db, self._session_user_map, session)
			case Action.DOWNLOAD_GAME_INIT:
				payload, ok, error = game_handlers.handle_download_game_init(message.payload, self._db, self._download_manager, self._session_user_map, session)
			case Action.DOWNLOAD_GAME_CHUNK:
				payload, ok, error = game_handlers.handle_download_game_chunk(message.payload, self._download_manager, self._session_user_map, session)
			case Action.DOWNLOAD_GAME_FINISH:
				payload, ok, error = game_handlers.handle_download_game_finish(message.payload, self._download_manager, self._session_user_map, session)
			case Action.CREATE_ROOM:
				payload, ok, error = room_handlers.handle_create_room(message.payload, self._room_manager, self._session_user_map, session)
			case Action.CHECK_MY_ROOM:
				payload, ok, error = room_handlers.handle_check_my_room(self._room_manager, self._session_user_map, session)
			case _:
				# Unknown action: echo payload, mark failed
				payload, ok, error = message.payload, False, "Unknown action"

		return Message.response(
			message.action,
			payload,
			msg_id=message.msg_id,
			ok=ok,
			error=error,
		)
