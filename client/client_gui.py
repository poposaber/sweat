import customtkinter
from .client_controller import ClientController
from .ui.login_page import LoginPage
from .ui.lobby_page import LobbyPage
from .client_state import ClientState

class ClientGUI:
    def __init__(self, root: customtkinter.CTk, client_controller: ClientController):
        super().__init__()
        self._client_controller = client_controller
        self._root = root
        self._root.title("Client GUI")
        self._root.geometry("800x600")

        self.status_label = customtkinter.CTkLabel(self._root, text="Disconnected", font=("Arial", 16))
        self.status_label.pack(pady=10)

        # Login page embedded
        self.login_page = LoginPage(self._root, login_callback=self._on_login_submit)
        # self.login_page.pack(pady=10)

        self.lobby_page = LobbyPage(self._root, logout_callback=self.logout)
        # Initially hide lobby page

        self._state_dict = {
            ClientState.DISCONNECTED: self.login_page, 
            ClientState.LOGGED_OUT: self.login_page,
            ClientState.IN_LOBBY: self.lobby_page
            }

        self._state = ClientState.DISCONNECTED
        
        self._set_state(self._state)

        # self.logout_button = customtkinter.CTkButton(self._root, text="Logout", command=self.logout)
        # self.logout_button.pack(pady=10)

        # self.disconnect_button = customtkinter.CTkButton(self, text="Disconnect", command=self.disconnect)
        # self.disconnect_button.pack(pady=10)

        # Optional: theme/appearance settings
        try:
            customtkinter.set_appearance_mode("System")
            customtkinter.set_default_color_theme("blue")
        except Exception:
            pass
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        # Auto-connect after GUI is constructed; controller should have GUI bound before mainloop runs
        self._root.after(0, self._auto_connect)

    def _set_state(self, new_state: ClientState):
        if new_state not in self._state_dict:
            raise ValueError(f"Invalid state: {new_state}")
        
        # Hide current view
        current_view = self._state_dict[self._state]
        current_view.pack_forget()
        # Show new view
        new_view = self._state_dict[new_state]
        new_view.pack(pady=10)
        self._state = new_state

    def _auto_connect(self):
        self.status_label.configure(text="Connecting...")
        self._client_controller.connect(
            on_result=lambda: self.status_label.configure(text="Connected"),
            on_error=lambda e: self.status_label.configure(text=f"Connect error: {e}"),
            on_disconnect=lambda: self.status_label.configure(text="Disconnected (Server closed)")
        )

    def _on_login_submit(self, username: str, password: str):
        def ok():
            self.status_label.configure(text="Logged In")
            self.login_page.set_error("")
            self._set_state(ClientState.IN_LOBBY)
        def ng(e: Exception):
            self.status_label.configure(text="Login failed")
            self.login_page.set_error(str(e))
        self._client_controller.login(username, password, on_result=ok, on_error=ng)

    def logout(self):
        def ok():
            self.status_label.configure(text="Logged Out")
            self._set_state(ClientState.LOGGED_OUT)
        self._client_controller.logout(on_result=ok,
                                      on_error=lambda e: self.status_label.configure(text=f"Logout error: {e}"))
        # self._set_state(ClientState.LOGGED_OUT)

    # def disconnect(self):
    #     self._client_controller.close()
    #     self.status_label.configure(text="Disconnected")

    def _on_close(self):
        self._root.destroy()
        self._client_controller.close()

    def mainloop(self):
        self._root.mainloop()
        