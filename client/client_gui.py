import customtkinter
from tkinter import messagebox
from .client_controller import ClientController
from .ui.views.entry_view import EntryView
from .ui.views.lobby_view import LobbyView
from .ui.views.developer_view import DeveloperView
from .client_state import ClientState
from protocol.enums import Role

class ClientGUI:
    def __init__(self, root: customtkinter.CTk, client_controller: ClientController):
        super().__init__()
        self._client_controller = client_controller
        self._root = root
        self._root.title("Client GUI")
        self._root.geometry("350x450")

        # Login page embedded
        self.entry_view = EntryView(self._root,
                                    login_callback=self._on_login_submit,
                                    register_callback=self._on_register_submit)
        # self.entry_view.pack(pady=10)

        self.lobby_view = LobbyView(self._root, logout_callback=self.logout)
        # Initially hide lobby page

        self.developer_view = DeveloperView(self._root, 
                                            logout_callback=self.logout, 
                                            upload_callback=self._on_upload_submit,
                                            my_works_callback=self._on_my_works_click)

        self._state_dict = {
            ClientState.DISCONNECTED: self.entry_view, 
            ClientState.LOGGED_OUT: self.entry_view,
            ClientState.IN_LOBBY: self.lobby_view, 
            ClientState.IN_DEVELOPMENT: self.developer_view,
            }

        self._state = ClientState.DISCONNECTED
        
        self._set_state(self._state)

        # Optional: theme/appearance settings
        try:
            customtkinter.set_appearance_mode("System")
            customtkinter.set_default_color_theme("blue")
        except Exception:
            pass
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        # Auto-connect after GUI is constructed; controller should have GUI bound before mainloop runs
        self._root.after(0, self._auto_connect)

    def _on_upload_submit(self, game_name: str, version: str, min_players: int, max_players: int, file_path: str):
        def on_success():
            messagebox.showinfo("Success", f"Game uploaded successfully!")
            
        def on_error(error_msg):
            messagebox.showerror("Error", f"Upload failed: {error_msg}")

        def on_progress(current, total):
            print(f"Upload progress: {current}/{total}")

        self._client_controller.upload_game(
            game_name, version, min_players, max_players, file_path,
            on_success, on_error, on_progress
        )

    def _set_state(self, new_state: ClientState):
        if new_state not in self._state_dict:
            raise ValueError(f"Invalid state: {new_state}")
        
        # Hide current view
        current_view = self._state_dict[self._state]
        current_view.place_forget()
        
        # Show new view
        new_view = self._state_dict[new_state]
        
        # Reset the view if it has a reset method (ensures clean state on re-entry)
        if hasattr(new_view, 'reset'):
            new_view.reset()
            
        new_view.place(relx=0.5, rely=0.5, relheight=1.0, relwidth=1.0, anchor=customtkinter.CENTER)
        self._state = new_state

        if hasattr(new_view, 'geom_size'):
            self._root.geometry(new_view.geom_size)

    def _on_connected(self):
        self._set_state(ClientState.LOGGED_OUT)
        self.entry_view.login_page.focus()
        # self.status_label.configure(text="Connected")

    def _auto_connect(self):
        # self.status_label.configure(text="Connecting...")
        self._client_controller.connect(
            on_result=self._on_connected,
        )

    def _on_login_submit(self, username: str, password: str, role: str):
        def ok():
            # self.status_label.configure(text=f"Logged In as {role}")
            self.entry_view.set_login_error("")
            self.entry_view.set_register_error("")
            if role == Role.PLAYER.value:
                self._set_state(ClientState.IN_LOBBY)
            elif role == Role.DEVELOPER.value:
                self._set_state(ClientState.IN_DEVELOPMENT)
                self._on_my_works_click()
            else:
                raise ValueError(f"Unknown role: {role}")
        def ng(e: Exception):
            # self.status_label.configure(text="Login failed")
            self.entry_view.set_login_error(str(e))
            self.entry_view.set_register_error("")
        self._client_controller.login(username, password, role, on_result=ok, on_error=ng)
        

    def _on_my_works_click(self):
        def ok(works: list[tuple[str, str, int, int]]):
            self.developer_view.set_my_works(works)
        def ng(e: Exception):
            messagebox.showerror("Error", f"Failed to fetch my works: {str(e)}")
        self._client_controller.fetch_my_works(on_result=ok, on_error=ng)

    def _on_register_submit(self, username: str, password: str, role: str):
        def ok():
            # self.status_label.configure(text=f"Registered as {role}")
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
            # self.status_label.configure(text="Registration failed")
            self.entry_view.set_login_error("")
            self.entry_view.set_register_error(str(e))
        self._client_controller.register(username, password, role, on_result=ok, on_error=ng)

    def logout(self):
        def ok():
            # self.status_label.configure(text="Logged Out")
            self._set_state(ClientState.LOGGED_OUT)
        def ng(e: Exception):
            messagebox.showerror("Error", f"Logout failed: {str(e)}")
        self._client_controller.logout(on_result=ok, on_error=ng)
        # self._set_state(ClientState.LOGGED_OUT)

    # def disconnect(self):
    #     self._client_controller.close()
    #     self.status_label.configure(text="Disconnected")

    def _on_close(self):
        self._root.destroy()
        self._client_controller.close()

    def mainloop(self):
        self._root.mainloop()
        