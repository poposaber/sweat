import socket
import struct
import logging
import threading
import select
from .errors import InteractionTimeoutError, FramedSocketError, DataTransmissionError, DisconnectedError

logger = logging.getLogger(__name__)

class FramedSocket:
    """
    a tcp socket connector doing 4-byte length-prefixed messages
    """
    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._send_lock = threading.Lock()
        self._recv_lock = threading.Lock()
        self._send_timeout: float | None = None
        self._recv_timeout: float | None = None

    @property
    def peer_address(self) -> tuple[str, int] | None:
        try:
            return self._sock.getpeername()
        except Exception:
            return None

    def send(self, data: bytes):
        try:
            length_prefix = struct.pack('!I', len(data))
            if self._send_timeout is not None:
                _, wlist, _ = select.select([], [self._sock], [], self._send_timeout)
                if not wlist:
                    peer = None
                    try:
                        peer = self._sock.getpeername()
                    except Exception:
                        peer = '<unknown>'
                    raise InteractionTimeoutError(f"Send timed out to {peer}")
            with self._send_lock:
                self._sock.sendall(length_prefix + data)
        except socket.timeout as e:
            peer = None
            try:
                peer = self._sock.getpeername()
            except Exception:
                peer = '<unknown>'
            raise InteractionTimeoutError(f"Send timed out to {peer}") from e
        except OSError as e:
            peer = None
            try:
                peer = self._sock.getpeername()
            except Exception:
                peer = '<unknown>'
            raise DataTransmissionError(f"Failed to send data to {peer}: {e}", cause=e, peer=str(peer)) from e
        except Exception as e:
            raise FramedSocketError("Unexpected error in send()") from e

    def receive(self) -> bytes:
        try:
            length_prefix = self._recv_exact(4)
        except DisconnectedError:
            raise
        except FramedSocketError:
            raise
        except Exception as e:
            raise FramedSocketError("Unexpected error while receiving length prefix") from e

        if not length_prefix:
            raise DisconnectedError("Socket disconnected while reading length prefix")
        message_length = struct.unpack('!I', length_prefix)[0]
        try:
            message = self._recv_exact(message_length)
        except DisconnectedError:
            raise
        except FramedSocketError:
            raise
        except Exception as e:
            raise FramedSocketError("Unexpected error while receiving message body") from e

        if not message:
            raise DisconnectedError("Socket disconnected while reading message data")
        return message
    
    def _recv_exact(self, num_bytes: int) -> bytes:
        buf = b''
        try:
            while len(buf) < num_bytes:
                # 若設定了接收超時，先用 select 等待可讀；避免影響 send 的一般 timeout
                if self._recv_timeout is not None:
                    # if self._sock.fileno() == -1: # socket closed
                    #     raise DisconnectedError("Socket is closed")
                    rlist, _, _ = select.select([self._sock], [], [], self._recv_timeout)
                    if not rlist:
                        peer = None
                        try:
                            peer = self._sock.getpeername()
                        except Exception:
                            peer = '<unknown>'
                        # logger.debug("Receive timed out waiting for data from %s", peer)
                        raise InteractionTimeoutError(f"Receive timed out from {peer}")
                with self._recv_lock:
                    chunk = self._sock.recv(num_bytes - len(buf))
                if not chunk:
                    logger.debug("Socket disconnected during receive (needed %d bytes, got %d)", num_bytes, len(buf))
                    raise DisconnectedError("Socket disconnected during receive")
                buf += chunk
            return buf
        except socket.timeout as e:
            peer = None
            try:
                peer = self._sock.getpeername()
            except Exception:
                peer = '<unknown>'
            raise InteractionTimeoutError(f"Receive timed out from {peer}") from e
        except DisconnectedError:
            # 允許往上層識別為正常斷線
            raise
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            # 這些錯誤代表連線已斷開，應轉為 DisconnectedError
            logger.debug("Connection reset/aborted during receive")
            raise DisconnectedError("Connection reset or aborted by peer")
        except OSError as e:
            # 針對 Windows/Linux 常見的連線重置錯誤碼進行額外檢查
            # 10054: Connection reset by peer
            # 10053: Software caused connection abort
            # 10038: Socket operation on non-socket (closed)
            if e.errno in (10054, 10053, 10038):
                logger.debug("OSError indicating disconnection during receive: %s", e)
                raise DisconnectedError(f"Connection lost: {e}") from e
            peer = None
            try:
                peer = self._sock.getpeername()
            except Exception:
                peer = '<unknown>'
            raise DataTransmissionError(f"Error receiving data from {peer}: {e}", cause=e, peer=str(peer)) from e
        except Exception as e:
            # 若 select 因為 socket 已關閉 (fileno=-1) 而拋出 ValueError，也視為斷線
            if isinstance(e, ValueError) and self._sock.fileno() == -1:
                raise DisconnectedError("Socket closed (fileno is -1)") from e
            raise FramedSocketError("Unexpected error in _recv_exact") from e
        
    def close(self):
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self._sock.close()
        except Exception as e:
            raise FramedSocketError("Error closing socket") from e
        
    # def settimeout(self, timeout: float | None):
    #     try:
    #         self._sock.settimeout(timeout)
    #         self._timeout = timeout
    #     except Exception as e:
    #         raise FramedSocketError("Error setting socket timeout") from e

    # def gettimeout(self) -> float | None:
    #     return self._timeout

    def set_recv_timeout(self, timeout: float | None):
        """Set per-receive timeout without touching socket-level timeout.

        使用 select 實作接收等待時間，避免影響 send 行為。
        """
        self._recv_timeout = timeout

    def get_recv_timeout(self) -> float | None:
        return self._recv_timeout
    
    def set_send_timeout(self, timeout: float | None):
        """Set per-send timeout without touching socket-level timeout.

        使用 select 實作接收等待時間，避免影響 receive 行為。
        """
        self._send_timeout = timeout

    def get_send_timeout(self) -> float | None:
        return self._send_timeout