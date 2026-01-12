import socket
import time
import threading
from ..common import protocol

MAX_PLAYERS = 2

class Server:
    def __init__(self, addr: tuple[str, int]):
        self._addr = addr
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(addr)
        self._sock.listen()
        # Limit to 2 concurrent clients
        self._connection_count = 0
        self._conn_count_lock = threading.Lock()
        self._stop_event = threading.Event()

    def stop(self):
        """Stop the server."""
        self._stop_event.set()
        try:
            self._sock.close()
        except Exception:
            pass

    def serve(self):
        """Accept connections in a loop and handle each in a dedicated thread."""
        self._sock.settimeout(1.0)
        printed = False
        while not self._stop_event.is_set():
            # Wait for a slot available (timeout to check stop_event)
            # acquired = self._semaphore.acquire(timeout=1.0)
            # if not acquired:
            #     continue

            try:
                if not printed:
                    print("READY")
                    printed = True
                session, addr = self._sock.accept()
                print(f"Accepted connection from {addr[0]}:{addr[1]}")
                with self._conn_count_lock:
                    self._connection_count += 1
                if self._connection_count >= MAX_PLAYERS:
                    print("max players reached, not accepting more connections")
                    try:
                        self._sock.close()
                    except Exception:
                        pass
                t = threading.Thread(target=self._client_loop, args=(session, addr), daemon=True)
                t.start()
            except socket.timeout:
                # No client connected within timeout, release slot and check stop_event
                # self._semaphore.release()
                continue
            except OSError:
                # Socket likely closed or error
                # self._semaphore.release()
                break
            except Exception as e:
                print(f"Accept error: {e}")
                # self._semaphore.release()
        while self._connection_count > 0:
            time.sleep(0.1)
    def _client_loop(self, session: socket.socket, addr: tuple[str, int]):
        """Per-connection loop: receive, dispatch, respond until error or stop."""
        try:
            while True:
                data = session.recv(1024)
                if not data:
                    print(f"Client {addr[0]}:{addr[1]} disconnected")
                    break
                
                msg = data.decode().strip()
                print(f"Received from {addr[0]}:{addr[1]}: {msg}")

                if msg == protocol.PING:
                    session.sendall(protocol.PONG.encode())
                elif msg == protocol.EXIT:
                    break
                else:
                    session.sendall(data)  # Echo back
        except Exception as e:
            print(f"Client {addr[0]}:{addr[1]} handler error: {e}")
        finally:
            session.close()
            with self._conn_count_lock:
                self._connection_count -= 1
            if self._connection_count == 0:
                print("No more connections, stopping server.")
                self.stop()



        