import customtkinter
from .client_controller import ClientController
from .ui.views.entry_view import EntryView
from .ui.views.lobby_view import LobbyView
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
        self.entry_view = EntryView(self._root,
                                    login_callback=self._on_login_submit,
                                    register_callback=self._on_register_submit)
        # self.entry_view.pack(pady=10)

        self.lobby_view = LobbyView(self._root, logout_callback=self.logout)
        # Initially hide lobby page

        self._state_dict = {
            ClientState.DISCONNECTED: self.entry_view, 
            ClientState.LOGGED_OUT: self.entry_view,
            ClientState.IN_LOBBY: self.lobby_view
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

    def _on_connected(self):
        self._set_state(ClientState.LOGGED_OUT)
        self.status_label.configure(text="Connected")

    def _auto_connect(self):
        self.status_label.configure(text="Connecting...")
        self._client_controller.connect(
            on_result=self._on_connected,
            on_error=lambda e: self.status_label.configure(text=f"Connect error: {e}"),
            on_disconnect=lambda: self.status_label.configure(text="Disconnected (Server closed)")
        )

    def _on_login_submit(self, username: str, password: str, role: str):
        def ok():
            self.status_label.configure(text=f"Logged In as {role}")
            self.entry_view.set_login_error("")
            self.entry_view.set_register_error("")
            self._set_state(ClientState.IN_LOBBY)
        def ng(e: Exception):
            self.status_label.configure(text="Login failed")
            self.entry_view.set_login_error(str(e))
            self.entry_view.set_register_error("")
        self._client_controller.login(username, password, role, on_result=ok, on_error=ng)

    def _on_register_submit(self, username: str, password: str, role: str):
        def ok():
            self.status_label.configure(text=f"Registered as {role}")
            self.entry_view.set_login_error("")
            self.entry_view.set_register_error("")
            
            # Sync role switch state from register page to login page
            # Note: role is passed as string ('player' or 'developer')
            if role == 'developer':
                self.entry_view.login_page.role_switch.select()
            else:
                self.entry_view.login_page.role_switch.deselect()
                
            self.entry_view.show_reg_success()
        def ng(e: Exception):
            self.status_label.configure(text="Registration failed")
            self.entry_view.set_login_error("")
            self.entry_view.set_register_error(str(e))
        self._client_controller.register(username, password, role, on_result=ok, on_error=ng)

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
        