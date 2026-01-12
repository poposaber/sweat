import socket

class Client:
    def __init__(self, addr: tuple[str, int]):
        self._host = addr[0]
        self._port = addr[1]
        self._sock = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))
        print(f"Connected to {self._host}:{self._port}")

    def send(self, message: str):
        if not self._sock:
            raise RuntimeError("Not connected")
        self._sock.sendall(message.encode())

    def receive(self) -> str:
        if not self._sock:
            raise RuntimeError("Not connected")
        data = self._sock.recv(1024)
        return data.decode()

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

        