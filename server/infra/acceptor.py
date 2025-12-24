import socket
from transport.framed_socket import FramedSocket
from session.session import Session


class Acceptor:
    def __init__(self, addr):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(addr)
        self._sock.listen(5)

    def accept(self) -> tuple[Session, tuple[str, int]]:
        client_sock, addr = self._sock.accept()
        connector = FramedSocket(client_sock)
        return Session(connector), addr

    def close(self):
        self._sock.close()