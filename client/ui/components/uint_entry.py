import customtkinter as ctk
import tkinter as tk

class UIntEntry(ctk.CTkEntry):
    def __init__(self, master, text="0", **kwargs):
        # Ensure we have a StringVar to trace
        self._var = kwargs.get("textvariable")
        if self._var is None:
            self._var = ctk.StringVar(value=text)
            kwargs["textvariable"] = self._var
            
        super().__init__(master, **kwargs)
        
        self._old_value = self._var.get()
        self._var.trace_add("write", self._trace_callback)

    def _trace_callback(self, *args):
        assert self._var is not None
        new_value = self._var.get()
    
        if new_value == "":
            self._var.set("0")
            self._old_value = "0"
            self.after_idle(lambda: self.icursor("end"))
            return
        
        # Check if valid unsigned integer
        if not new_value.isdigit():
            self._var.set(self._old_value)
            return

        # Disallow leading zeros unless it's just "0"
        if len(new_value) > 1 and new_value.startswith("0"):
             new_value = new_value.lstrip("0")
             if new_value == "":
                 new_value = "0"
             self._var.set(new_value)
             self._old_value = new_value
             return
             
        self._old_value = new_value