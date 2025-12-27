import customtkinter
from typing import Callable, Optional
import tkinter
from ..pages.login_page import LoginPage
from ..pages.register_page import RegisterPage
from ..pages.reg_success_page import RegSuccessPage
from ..components.clickable_label import ClickableLabel
from enum import Enum

class EntryViewState(Enum):
    LOGIN = 1
    REGISTER = 2
    REG_SUCCESS = 3

class EntryView(customtkinter.CTkFrame):
    def __init__(self, master, login_callback: Optional[Callable[[str, str, str], None]] = None,
                 register_callback: Optional[Callable[[str, str, str], None]] = None):
        super().__init__(master, width=400, height=500)
        
        self.login_page = LoginPage(self, login_callback=login_callback)
        self.login_page.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.register_page = RegisterPage(self, register_callback=register_callback)
        # self.register_page.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        # self.register_page.lower()

        self.prompt_text = customtkinter.CTkLabel(master=self, text="Don't have an account?", font=("Arial", 11))
        self.prompt_text.place(relx=0.65, rely=0.95, anchor=tkinter.CENTER)

        self.swap_label = ClickableLabel(master=self, text="Register", font=("Arial", 11, "underline"), command=self.swap)
        self.swap_label.place(relx=0.9, rely=0.95, anchor=tkinter.CENTER)

        self.reg_success_page = RegSuccessPage(self, continue_callback=self.continue_to_login)

        self._state = EntryViewState.LOGIN

        self._page_dict = {
            EntryViewState.LOGIN: self.login_page,
            EntryViewState.REGISTER: self.register_page,
            EntryViewState.REG_SUCCESS: self.reg_success_page
        }

    def set_state(self, state: EntryViewState):
        if state not in self._page_dict:
            raise ValueError(f"Invalid state: {state}")
        for page in self._page_dict.values():
            page.place_forget()
        page_to_show = self._page_dict[state]
        page_to_show.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self._state = state
    
    def swap(self):
        if self._state == EntryViewState.LOGIN:
            self.set_state(EntryViewState.REGISTER)
            self.set_to_login_prompt()
            self.register_page.focus()
        else:
            self.set_state(EntryViewState.LOGIN)
            self.set_to_register_prompt()
            self.login_page.focus()
        self.reset()

    def show_reg_success(self):
        self.set_state(EntryViewState.REG_SUCCESS)
        self.prompt_text.place_forget()
        self.swap_label.place_forget()

    def continue_to_login(self):
        self.set_state(EntryViewState.LOGIN)
        self.set_to_register_prompt()
        self.login_page.focus()
        self.prompt_text.place(relx=0.65, rely=0.95, anchor=tkinter.CENTER)
        self.swap_label.place(relx=0.9, rely=0.95, anchor=tkinter.CENTER)

    def set_login_error(self, message: str):
        self.login_page.set_error(message)

    def set_register_error(self, message: str):
        self.register_page.set_error(message)

    def set_to_login_prompt(self):
        self.prompt_text.configure(text="Already have an account?")
        self.swap_label.set_text("Login")

    def set_to_register_prompt(self):
        self.prompt_text.configure(text="Don't have an account?")
        self.swap_label.set_text("Register")

    def reset(self):
        self.login_page.reset()
        self.register_page.reset()