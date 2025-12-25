import argparse
import logging
from .client_controller import ClientController
import customtkinter
from .client_gui import ClientGUI


def main():
	parser = argparse.ArgumentParser(description="Start the Client GUI")
	parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
	parser.add_argument("--port", type=int, default=14253, help="Server port (default: 14253)")
	parser.add_argument(
		"--log-level",
		default="INFO",
		choices=["DEBUG", "INFO", "WARNING", "ERROR"],
		help="Logging level (default: INFO)",
	)
	parser.add_argument("--trace-io", action="store_true", help="Trace sent/received messages (client-side)")
	args = parser.parse_args()

	logging.basicConfig(level=getattr(logging, args.log_level), format='%(asctime)s %(levelname)s [%(name)s] %(message)s')
	# Create controller first without GUI, then bind GUI to controller to avoid circular init
	root = customtkinter.CTk()
	controller = ClientController(addr=(args.host, args.port), gui=root, trace_io=args.trace_io)
	app = ClientGUI(root=root, client_controller=controller)
	# controller.set_gui(app)

	app.mainloop()


if __name__ == "__main__":
	main()
# from .client_controller import ClientController
# from .client_gui import ClientGUI

# controller = ClientController(addr=("127.0.0.1", 