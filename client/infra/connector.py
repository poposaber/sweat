import socket
import logging
from transport.framed_socket import FramedSocket
from session.session import Session
from .errors import ConnectionTimeoutError, ConnectorError
import time

logger = logging.getLogger(__name__)


class Connector:
    def __init__(self, addr):
        self._addr = addr

    def connect(self, connect_timeout: float | None = None, max_attempts: int = 3) -> Session:
        """Create a socket, connect with optional connect_timeout, then set io_timeout for send/recv.

        - connect_timeout: seconds to wait for connect()
        - io_timeout: per-operation timeout (send/recv); if None socket is blocking
        """
        
        attempts = 1
        while True:
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                if connect_timeout is not None:
                    temp_sock.settimeout(connect_timeout)
                logger.info(f"Attempting to connect to {self._addr}, attempt {attempts}")
                temp_sock.connect(self._addr)
                break  # success
            except socket.timeout as e:
                logger.exception("connect() timed out to %s", self._addr)
                temp_sock.close()
                
                if attempts >= max_attempts:
                    raise ConnectionTimeoutError(f"Connect to {self._addr} timed out") from e
                attempts += 1
                time.sleep(1)  # brief pause before retry
            except OSError as e:
                logger.exception("connect() failed to %s", self._addr)
                temp_sock.close()
                
                if attempts >= max_attempts:
                    raise ConnectorError(f"Connect failed to {self._addr}: {e}") from e
                attempts += 1
                time.sleep(1)  # brief pause before retry
            except Exception as e:
                logger.exception("Unexpected error during connect() to %s", self._addr)
                temp_sock.close()
                
                if attempts >= max_attempts:
                    raise ConnectorError(f"Unexpected error during connect to {self._addr}: {e}") from e
                attempts += 1
                time.sleep(1)  # brief pause before retry
            
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