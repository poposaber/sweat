import argparse
import sys
from .client import Client
from common import protocol

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8972)
    parser.add_argument("--username", default="Player")
    args = parser.parse_args()

    client = Client((args.host, args.port), args.username)

    try:
        client.connect()
        
        while True:
            # Simple interactive mode
            try:
                msg = input("Enter message (PING to ping, EXIT to quit): ").strip()
            except EOFError:
                break

            if not msg:
                continue
            
            # Map user input to protocol if needed, or just send raw
            if msg.upper() == "PING":
                to_send = protocol.PING
            elif msg.upper() == "EXIT":
                to_send = protocol.EXIT
            else:
                to_send = msg

            client.send(to_send)
            
            if to_send == protocol.EXIT:
                break
            
            data = client.receive()
            print(f"Server replied: {data}")
            
    except Exception as e:
        print(f"Client Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
