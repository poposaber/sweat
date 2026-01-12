import argparse
import threading
import time

from .server import Server

def main():
    parser = argparse.ArgumentParser(description="Server main entry point")
    parser.add_argument("--port", type=int, default=8972, help="Port to run the server on")
    # Add arguments here if needed
    args = parser.parse_args()
    port = args.port if args else 8972
    server = Server(("127.0.0.1", port))
    
    # Run server in a separate thread
    server_thread = threading.Thread(target=server.serve, daemon=True)
    server_thread.start()
    
    # print("Type 'quit' to stop the server.")
    # try:
    #     while True:
    #         cmd = input()
    #         if cmd.strip().lower() in ["quit", "exit", "q"]:
    #             print("Stopping server...")
    #             server.stop()
    #             server_thread.join(timeout=2.0)
    #             break
    # except KeyboardInterrupt:
    #     print("Stopping server...")
    #     server.stop()
    #     server_thread.join(timeout=2.0)
    server_thread.join()

if __name__ == "__main__":
    main()