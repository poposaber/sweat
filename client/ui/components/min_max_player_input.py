import customtkinter as ctk
from .uint_spinner import UIntSpinner

class MinMaxPlayerInput(ctk.CTkFrame):
    def __init__(self, master, width: int = 200, height: int = 30):
        super().__init__(master, width=width, height=height, fg_color="transparent")

        self.min_spinner = UIntSpinner(self, width=80, height=height, placeholder="Min", 
                                       min_value=1, max_value=100, command=self._on_min_change)
        self.min_spinner.place(relx=0.2, rely=0.5, anchor=ctk.CENTER)

        self.to_label = ctk.CTkLabel(self, text="to")
        self.to_label.place(relx=0.4, rely=0.5, anchor=ctk.CENTER)

        self.max_spinner = UIntSpinner(self, width=80, height=height, placeholder="Max", 
                                       min_value=1, max_value=100, command=self._on_max_change)
        self.max_spinner.place(relx=0.6, rely=0.5, anchor=ctk.CENTER)

        self.player_label = ctk.CTkLabel(self, text="players")
        self.player_label.place(relx=0.85, rely=0.5, anchor=ctk.CENTER)
        
        # Initialize values
        self.min_spinner.set_value(1)
        self.max_spinner.set_value(1)

    def _on_min_change(self, value: int):
        max_val = self.max_spinner.get_value()
        
        # If manual input made min > max, clamp min to max
        if value > max_val:
            self.min_spinner.set_value(max_val)
            return

        # Update max_spinner's lower bound
        self.max_spinner.min_value = value
        
        # If max is somehow less than new min (should be handled by set_value clamping, but good to be sure)
        if self.max_spinner.get_value() < value:
            self.max_spinner.set_value(value)

    def _on_max_change(self, value: int):
        min_val = self.min_spinner.get_value()
        
        # If manual input made max < min, clamp max to min
        if value < min_val:
            self.max_spinner.set_value(min_val)
            return

        # Update min_spinner's upper bound
        self.min_spinner.max_value = value
        
        # If min is somehow greater than new max
        if self.min_spinner.get_value() > value:
            self.min_spinner.set_value(value)

    def get_min_max(self) -> tuple[int, int]:
        return (self.min_spinner.get_value(), self.max_spinner.get_value())