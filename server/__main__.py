import argparse
import logging
from .server_cli import ServerCLI


def main():
	parser = argparse.ArgumentParser(description="Start the TCP server")
	parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
	parser.add_argument("--port", type=int, default=14253, help="Bind port (default: 14253)")
	parser.add_argument(
		"--log-level",
		default="INFO",
		choices=["DEBUG", "INFO", "WARNING", "ERROR"],
		help="Logging level (default: INFO)",
	)
	parser.add_argument(
		"--trace-io",
		action="store_true",
		help="Trace sent/received messages (server-side)",
	)
	args = parser.parse_args()

	logging.basicConfig(
		level=getattr(logging, args.log_level),
		format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
	)

	server = ServerCLI((args.host, args.port), trace_io=args.trace_io)
	try:
		server.run()
	finally:
		pass


if __name__ == "__main__":
	main()
