import logging
from typing import Optional
from threading import Thread
from .server import Server

class ServerCLI:
    def __init__(self, addr: tuple[str, int], trace_io: bool = False):
        self._server = Server(addr, trace_io=trace_io)
        self._thread: Optional[Thread] = None

    def run(self):
        self._thread = Thread(target=self._server.serve, daemon=True)
        self._thread.start()
        try:
            while True:
                cmd = input("Enter 'quit' to stop, 'status' to check: ").strip().lower()
                if cmd in ("quit", "exit", "q"):
                    break
                elif cmd == "status":
                    print("Server is running...")
                elif cmd == "":
                    continue
                else:
                    print("Unknown command. Type 'status' or 'quit'.")
        except KeyboardInterrupt:
            print("\nStopping server...")
        finally:
            self._server.stop()
            if self._thread:
                self._thread.join(timeout=2.0)

    def _close(self):
        # Kept for backward compatibility; prefer stop() in run()
        self._server.close()