import logging
import queue
from typing import Callable, Optional
from transport.framed_socket import FramedSocket
from protocol.message import Message
from protocol.enums import MessageType
from protocol.json_codec import encode as encode_message, decode as decode_message
from .errors import SessionError, SessionTimeoutError, SessionDisconnectedError
from transport.errors import InteractionTimeoutError, DisconnectedError
import threading

logger = logging.getLogger(__name__)
class Session:
    def __init__(self, fsock: FramedSocket):
        self._fsock = fsock
        self._event_queue: queue.Queue[Message] = queue.Queue()
        self._response_dict: dict[str, Message] = {}
        self._cond = threading.Condition()
        self._stop_event = threading.Event()
        self.recv_message_thread: Optional[threading.Thread] = None
        self._on_event: Optional[Callable[[Message], None]] = None
        self._on_disconnect: Optional[Callable[[], None]] = None
        self._rxloop_prev_timeout: float | None = None
        self._user_timeout: float | None = None
        self._trace_io: bool = False

    def set_trace_io(self, enabled: bool) -> None:
        self._trace_io = bool(enabled)

    def send_message(self, message: Message):
        try:
            data = encode_message(message)
            if self._trace_io:
                logger.info("TX %s", data.decode("utf-8"))
            self._fsock.send(data)
        except InteractionTimeoutError as e:
            raise SessionTimeoutError("send_message timed out") from e
        except Exception as e:
            # 不在下層記 exception，改由呼叫端/邊界統一記錄
            raise SessionError("send_message failed") from e

    def receive_message(self) -> Message:
        try:
            data = self._fsock.receive()
            message = decode_message(data)
            if self._trace_io:
                logger.info("RX %s", data.decode("utf-8"))
            return message
        except InteractionTimeoutError as e:
            # 接收超時屬於「暫時無資料」，上層可選擇重試或忽略
            raise SessionTimeoutError("receive_message timed out") from e
        except DisconnectedError as e:
            # 將正常斷線轉為高層 SessionDisconnectedError，
            # 伺服器端可降級記錄、客戶端可視情況提示或重連。
            raise SessionDisconnectedError("disconnected") from e
        except Exception as e:
            # 不在下層記 exception，改由呼叫端/邊界統一記錄
            raise SessionError("receive_message failed") from e
    
    def request_response(self, message: Message, *, on_event: Optional[Callable[[Message], None]] = None) -> Message:
        """Send a request and wait until the matching response is received.

        Any non-matching messages received during the wait are treated as events.
        If `on_event` is provided, it will be invoked for each such message; otherwise,
        they are queued and can be retrieved later via `poll_event()`.
        """
        req_id = message.msg_id
        if not req_id:
            # Defensive: although Message.request always sets msg_id
            logger.debug("request_response called with message without msg_id; sending anyway")
        # If background recv loop is running, coordinate via condition + response_dict
        if self.recv_message_thread is not None and self.recv_message_thread.is_alive():
            self.send_message(message)
            with self._cond:
                while req_id not in self._response_dict:
                    self._cond.wait()
                resp = self._response_dict.pop(req_id)
                return resp
        # Fallback: do inline receive loop
        self.send_message(message)
        while True:
            try:
                incoming = self.receive_message()
            except SessionTimeoutError:
                # 無資料，繼續等待
                continue
            if incoming.type == MessageType.RESPONSE and incoming.msg_id == req_id:
                return incoming
            try:
                if on_event is not None:
                    on_event(incoming)
                else:
                    self._event_queue.put(incoming)
            except Exception:
                logger.exception("on_event callback raised")
    
    def close(self):
        try:
            self.stop_recv_loop()
            self._fsock.close()
        except Exception as e:
            # 不在下層記 exception，改由呼叫端/邊界統一記錄
            raise SessionError("close failed") from e
        
    def settimeout(self, timeout: float | None):
        """Set socket IO timeout.

        若背景接收迴圈正在執行，為了維持可快速退出的短超時（例如 0.2s），
        此處不會立刻更動底層 socket 的 timeout；而是記錄使用者期望值，
        並在 `stop_recv_loop()` 時優先套用。這可避免把接收迴圈改回阻塞狀態。
        """
        if self.recv_message_thread is not None and self.recv_message_thread.is_alive():
            self._user_timeout = timeout
            logger.debug("settimeout deferred while recv loop running; will apply on stop: %s", timeout)
            return
        try:
            self._fsock.settimeout(timeout)
            self._user_timeout = None
        except Exception as e:
            # 不在下層記 exception，改由呼叫端/邊界統一記錄
            raise SessionError("settimeout failed") from e
    
    def poll_event(self) -> Message | None:
        """Retrieve one queued event message, if any."""
        try:
            return self._event_queue.get_nowait()
        except queue.Empty:
            return None

    # --- Background receive loop management ---
    def start_recv_loop(self, *, on_event: Optional[Callable[[Message], None]] = None, on_disconnect: Optional[Callable[[], None]] = None) -> None:
        """Start background receive loop that routes responses and events.

        If `on_event` provided, it's called for each event; otherwise events are enqueued.
        If `on_disconnect` provided, it's called when the session is disconnected.
        Safe to call multiple times; only starts if not already running.
        """
        if self.recv_message_thread is not None and self.recv_message_thread.is_alive():
            return
        self._on_event = on_event
        self._on_disconnect = on_disconnect
        self._stop_event.clear()
        # 為了能在 stop 時快速退出阻塞的 recv，將接收設為短超時（不影響 send）
        try:
            # 儲存舊值並設為短接收超時（例如 0.2s）
            self._rxloop_prev_timeout = self._fsock.gettimeout()
            self._rxloop_prev_recv_timeout = self._fsock.get_recv_timeout()
            self._fsock.set_recv_timeout(0.2)
        except Exception:
            # 若設置失敗，不影響主流程；只是可能需要靠 join 超時結束
            pass
        t = threading.Thread(target=self._recv_loop, name="SessionRecvLoop", daemon=True)
        self.recv_message_thread = t
        t.start()

    def stop_recv_loop(self) -> None:
        if self.recv_message_thread is None:
            return
        self._stop_event.set()
        # Waking up the thread if it's blocked on socket happens when socket closes
        try:
            self.recv_message_thread.join(timeout=2.0)
        except Exception:
            pass
        finally:
            self.recv_message_thread = None
            # 恢復原本的 io timeout 或套用 deferred 使用者設定，並恢復接收超時
            try:
                if self._user_timeout is not None:
                    self._fsock.settimeout(self._user_timeout)
                else:
                    self._fsock.settimeout(self._rxloop_prev_timeout)
                self._fsock.set_recv_timeout(self._rxloop_prev_recv_timeout)
            except Exception:
                pass
            finally:
                self._user_timeout = None
                self._rxloop_prev_timeout = None
                self._rxloop_prev_recv_timeout = None

    def _recv_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                incoming = self.receive_message()
            except SessionTimeoutError:
                # Timeout means no data received yet, just continue checking stop_event
                continue
            except SessionDisconnectedError:
                # Server closed the connection, break the loop
                logger.info("Session disconnected in background loop")
                if self._on_disconnect:
                    try:
                        self._on_disconnect()
                    except Exception:
                        logger.exception("on_disconnect callback raised")
                break
            except SessionError:
                # Other session errors, log and continue
                continue
            try:
                # Route by type / correlation id
                if incoming.type == MessageType.RESPONSE and incoming.msg_id:
                    with self._cond:
                        self._response_dict[incoming.msg_id] = incoming
                        self._cond.notify_all()
                else:
                    if self._on_event is not None:
                        try:
                            self._on_event(incoming)
                        except Exception as e:
                            logger.exception(f"on_event callback raised in recv loop: {e}")
                    else:
                        self._event_queue.put(incoming)
            except Exception as e:
                logger.exception(f"Unexpected error in recv loop routing: {e}")