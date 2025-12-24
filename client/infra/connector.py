import socket
import logging
from transport.framed_socket import FramedSocket
from session.session import Session
from .errors import ConnectionTimeoutError, ConnectorError

logger = logging.getLogger(__name__)


class Connector:
    def __init__(self, addr):
        self._addr = addr

    def connect(self, connect_timeout: float | None = None) -> Session:
        """Create a socket, connect with optional connect_timeout, then set io_timeout for send/recv.

        - connect_timeout: seconds to wait for connect()
        - io_timeout: per-operation timeout (send/recv); if None socket is blocking
        """
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if connect_timeout is not None:
                temp_sock.settimeout(connect_timeout)
            temp_sock.connect(self._addr)
        except socket.timeout as e:
            logger.exception("connect() timed out to %s", self._addr)
            temp_sock.close()
            raise ConnectionTimeoutError(f"Connect to {self._addr} timed out") from e
        except OSError as e:
            logger.exception("connect() failed to %s", self._addr)
            temp_sock.close()
            raise ConnectorError(f"Connect failed to {self._addr}: {e}") from e
        finally:
            # restore blocking mode or leave as-is; we'll set io_timeout below
            try:
                temp_sock.settimeout(None)
            except Exception:
                pass

        # set per-operation timeout for send/recv if requested
        # if io_timeout is not None:
        #     try:
        #         temp_sock.settimeout(io_timeout)
        #     except Exception:
        #         logger.exception("Failed to set io_timeout on socket for %s", self._addr)

        connector = FramedSocket(temp_sock)
        return Session(connector)