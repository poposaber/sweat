import customtkinter
from .client_controller import ClientController
from .ui.login_page import LoginPage

class ClientGUI(customtkinter.CTk):
    def __init__(self, client_controller: ClientController):
        super().__init__()
        self.client_controller = client_controller
        self.title("Client GUI")
        self.geometry("800x600")

        self.status_label = customtkinter.CTkLabel(self, text="Disconnected", font=("Arial", 16))
        self.status_label.pack(pady=10)

        # Login page embedded
        self.login_page = LoginPage(self, login_callback=self._on_login_submit)
        self.login_page.pack(pady=10)

        self.logout_button = customtkinter.CTkButton(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        # self.disconnect_button = customtkinter.CTkButton(self, text="Disconnect", command=self.disconnect)
        # self.disconnect_button.pack(pady=10)

        # Optional: theme/appearance settings
        try:
            customtkinter.set_appearance_mode("System")
            customtkinter.set_default_color_theme("blue")
        except Exception:
            pass
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # Auto-connect after GUI is constructed; controller should have GUI bound before mainloop runs
        self.after(0, self._auto_connect)

    def _auto_connect(self):
        self.status_label.configure(text="Connecting...")
        self.client_controller.connect(
            on_result=lambda: self.status_label.configure(text="Connected"),
            on_error=lambda e: self.status_label.configure(text=f"Connect error: {e}"),
            on_disconnect=lambda: self.status_label.configure(text="Disconnected (Server closed)")
        )

    def _on_login_submit(self, username: str, password: str):
        def ok():
            self.status_label.configure(text="Logged In")
            self.login_page.set_error("")
        def ng(e: Exception):
            self.status_label.configure(text="Login failed")
            self.login_page.set_error(str(e))
        self.client_controller.login(username, password, on_result=ok, on_error=ng)

    def logout(self):
        self.client_controller.logout(on_result=lambda: self.status_label.configure(text="Logged Out"),
                                      on_error=lambda e: self.status_label.configure(text=f"Logout error: {e}"))

    # def disconnect(self):
    #     self.client_controller.close()
    #     self.status_label.configure(text="Disconnected")

    def _on_close(self):
        self.destroy()
        self.client_controller.close()
        