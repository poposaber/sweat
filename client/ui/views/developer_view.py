import customtkinter as ctk
from typing import Callable, Optional
from ..pages.my_works_page import MyWorksPage
from ..pages.upload_page import UploadPage
from ..pages.account_page import AccountPage
from ..components.tabbar import TabBar

class DeveloperView(ctk.CTkFrame):
    def __init__(self, master, logout_callback: Optional[Callable[[], None]] = None, upload_callback: Optional[Callable[[str, str, int, int, str], None]] = None):
        super().__init__(master)

        # ctk.CTkLabel(self, text="Developer View").place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
        # ctk.CTkButton(
        #     self, text="Logout",
        #     command=logout_callback
        # ).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.my_works_page = MyWorksPage(self)
        self.upload_page = UploadPage(self, on_upload_callback=upload_callback)
        self.account_page = AccountPage(self, logout_callback=logout_callback)
        self.tab_bar = TabBar(self, command=self._on_tabbar_click)
        self.tab_bar.add_tab("my_works", "My Works", self.my_works_page, default=True)
        self.tab_bar.add_tab("upload", "Upload", self.upload_page)
        self.tab_bar.add_tab("account", "Account", self.account_page)
        self.tab_bar.place_default()

        self.geom_size = "800x600"

    def _on_tabbar_click(self, id: str):
        print(f"DeveloperView: Tab '{id}' clicked.")

    def reset(self):
        self.tab_bar.show("my_works")