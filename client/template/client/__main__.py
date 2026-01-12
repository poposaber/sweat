import argparse
import sys
from .client import Client

# Try to import protocol from common
try:
    from ..common import protocol
except ImportError:
    # Fallback if running as script without package context (though -m recommended)
    try:
        from client.template.common import protocol
    except ImportError:
        print("Could not import protocol. Run from root with -m client.template.client")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8972)
    args = parser.parse_args()

    client = Client((args.host, args.port))

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
