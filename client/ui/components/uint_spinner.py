import customtkinter as ctk
from .uint_entry import UIntEntry
from typing import Callable, Optional

class UIntSpinner(ctk.CTkFrame):
    def __init__(self, master, width: int = 100, height: int = 30, placeholder: str = "0", 
                 min_value: int = 0, max_value: int = 100, step: int = 1, 
                 command: Optional[Callable[[int], None]] = None):
        super().__init__(master, width=width, height=height, fg_color="transparent")

        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.command = command

        # Use StringVar for easier text management
        self.value_var = ctk.StringVar(value=str(min_value))

        self.decrement_btn = ctk.CTkButton(self, text="-", command=self.decrement)
        self.decrement_btn.place(relx=0, rely=0, relwidth=0.3, relheight=1, anchor=ctk.NW)

        self.value_entry = UIntEntry(self, placeholder_text=placeholder, textvariable=self.value_var)
        self.value_entry.place(relx=0.5, rely=0.5, relwidth=0.4, relheight=1, anchor=ctk.CENTER)
        
        # Bind events for manual entry
        self.value_entry.bind("<FocusOut>", self._on_entry_change)
        self.value_entry.bind("<Return>", self._on_entry_change)

        self.increment_btn = ctk.CTkButton(self, text="+", command=self.increment)
        self.increment_btn.place(relx=1, rely=0, relwidth=0.3, relheight=1, anchor=ctk.NE)

    def get_value(self) -> int:
        try:
            text = self.value_var.get()
            if not text:
                return self.min_value
            return int(text)
        except ValueError:
            return self.min_value

    def set_value(self, value: int):
        # Clamp value
        value = max(self.min_value, min(value, self.max_value))
        
        # Update variable if different
        if self.value_var.get() != str(value):
            self.value_var.set(str(value))
        
        if self.command:
            self.command(value)

    def increment(self):
        current = self.get_value()
        if current + self.step <= self.max_value:
            self.set_value(current + self.step)
        else:
            self.set_value(self.max_value)

    def decrement(self):
        current = self.get_value()
        if current - self.step >= self.min_value:
            self.set_value(current - self.step)
        else:
            self.set_value(self.min_value)

    def _on_entry_change(self, event=None):
        # If empty, leave it empty (showing placeholder)
        # if not self.value_var.get():
        #     return

        current = self.get_value()
        # Clamp and update if necessary
        if current < self.min_value:
            self.set_value(self.min_value)
        elif current > self.max_value:
            self.set_value(self.max_value)
        else:
            # Even if valid, we might want to trigger command
            if self.command:
                self.command(current)