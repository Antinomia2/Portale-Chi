import tkinter as tk
from tkinter import ttk

class EntrySuggestion(ttk.Frame):
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(parent)
        self.values = values or []
        self.var = tk.StringVar()

        self.entry = ttk.Entry(self, textvariable=self.var, **kwargs)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.columnconfigure(0, weight=1)

        self.lb = tk.Listbox(self, height=6)
        self.lb.bind("<<ListboxSelect>>", self._on_select)
        self.entry.bind("<KeyRelease>", self._on_key)

    def set_values(self, values):
        self.values = values

    def get(self):
        return self.var.get()

    def enable(self, flag=True):
        state = "normal" if flag else "disabled"
        self.entry.configure(state=state)
        if not flag:
            self._hide_list()

    def _on_key(self, _):
        s = self.get().lower().strip()
        self.lb.delete(0, tk.END)
        if not s:
            self._hide_list()
            return
        for v in self.values:
            if s in str(v).lower():
                self.lb.insert(tk.END, v)
        if self.lb.size():
            self.lb.grid(row=1, column=0, sticky="ew")
        else:
            self._hide_list()

    def _on_select(self, _):
        if self.lb.curselection():
            self.var.set(self.lb.get(self.lb.curselection()))
        self._hide_list()

    def _hide_list(self):
        self.lb.grid_remove()