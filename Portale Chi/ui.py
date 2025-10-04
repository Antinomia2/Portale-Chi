import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import requests
from entrysuggestion import EntrySuggestion
import config
import core
import utils

COLUMNS = ("Data", "Ora", "Aula", "Tipo d'esame")
FACOLTA = core.load_facolta()

class Ui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portale Chi")
        self.geometry("820x520")
        self.resizable(False, False)

        self.options = {}
        self.data = None
        self.url_corsi = config.URL_CORSI
        self.today = utils.get_today()
        self.ayear_later = utils.get_ayear_later(self.today)

        self._build_header()
        self._build_row_facolta()
        self._build_row_corso()
        self._build_table()

    def _build_header(self):
        ttk.Label(
            self,
            text="Flusso : Digita facoltà ->  Click Avvia -> Digita corso -> Click Mostra",
            font=("Segoe UI", 12),
        ).pack(anchor="w", padx=10, pady=(24, 4))

        self.main = ttk.Frame(self, padding=10)
        self.main.pack(fill="both", expand=True)
        self.main.columnconfigure(1, weight=1)

    def _build_row_facolta(self):
        ttk.Label(self.main, text="Facoltà", font=("Segoe UI", 11)).grid(
            row=0, column=0, sticky="w", pady=(4, 0)
        )
        self.fac_entry = EntrySuggestion(self.main, values=FACOLTA)
        self.fac_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8))

        self.btn_avvia = ttk.Button(self.main, text="Avvia", command=self.on_avvia)
        self.btn_avvia.grid(row=1, column=2, sticky="e")

    def _build_row_corso(self):
        ttk.Label(self.main, text="Corso", font=("Segoe UI", 11)).grid(
            row=2, column=0, sticky="w", pady=(16, 0)
        )
        self.corso_entry = EntrySuggestion(self.main, values=[])
        self.corso_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 8))

        self.btn_mostra = ttk.Button(self.main, text="Mostra", command=self.on_mostra)
        self.btn_mostra.grid(row=3, column=2, sticky="e")

        self.pb = ttk.Progressbar(self.main, mode="indeterminate")

        self._set_corso_enabled(False)
        self._set_button_mostra(False)

    def _build_table(self):
        self.tree = ttk.Treeview(self.main, columns=COLUMNS, show="headings", height=8)
        for c in COLUMNS:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=130, anchor="center")
        self.tree.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(28, 0))
        self.main.rowconfigure(6, weight=1)

    def _clear_table(self):
        items = self.tree.get_children()
        if items:
            self.tree.delete(*items)

    def _show_progress(self):
        self.pb.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(16, 0))
        self.pb.start(10)

    def _hide_progress(self):
        self.pb.stop()
        self.pb.grid_remove()

    def _set_facolta_enabled(self, flag: bool):
        self.fac_entry.enable(flag)
        self.btn_avvia.state(["!disabled"] if flag else ["disabled"])

    def _set_corso_enabled(self, flag: bool):
        self.corso_entry.enable(flag)

    def _set_button_mostra(self, flag: bool):
        self.btn_mostra.state(["!disabled"] if flag else ["disabled"])

    def _disable_all(self):
        self._set_facolta_enabled(False)
        self._set_corso_enabled(False)
        self._set_button_mostra(False)

    def _post_fetch_ok(self, opzioni_presenti: bool):
        self._set_facolta_enabled(True)
        if opzioni_presenti:
            self._set_corso_enabled(True)
            self._set_button_mostra(True)
        else:
            self._set_corso_enabled(False)
            self._set_button_mostra(False)

    def on_avvia(self):
        fac_key = self.fac_entry.get().strip()

        if not fac_key:
            messagebox.showwarning("Attenzione", "Campo vuoto, inserisci una facoltà!")
            return
        if fac_key not in FACOLTA:
            messagebox.showwarning("Attenzione", "La facoltà inserita non è valida!")
            return

        self._disable_all()
        self.corso_entry.var.set("")
        self._clear_table()
        self._show_progress()

        threading.Thread(target=self._launch_worker, args=(fac_key,), daemon=True).start()

    def _launch_worker(self, fac_key):
        payload = core.build_payload(fac_key, self.today, self.ayear_later, FACOLTA)
        req = requests.post(self.url_corsi, data=payload)
        data_local = json.loads(req.text)
        opzioni_local = core.get_corsi(data_local)

        def _apply():
            self._hide_progress()

            self.data = data_local
            self.options.clear()
            self.options.update(opzioni_local)

            if self.options:
                self.corso_entry.set_values(self.options)
                self._post_fetch_ok(True)
            else:
                self._post_fetch_ok(False)
                messagebox.showinfo("Avviso", "Nessun esame trovato per questa facoltà!")

        self.after(0, _apply)

    def on_mostra(self):
        corso_key = self.corso_entry.get().strip()

        if not corso_key:
            messagebox.showwarning("Attenzione", "Campo vuoto, inserisci un corso!")
            return
        if corso_key not in self.options:
            messagebox.showwarning("Attenzione", "Il corso inserito non è valido!")
            return

        self._clear_table()

        key_codice = self.options[corso_key]
        corso = self.data["Insegnamenti"][key_codice]

        row = []
        for appello in corso["Appelli"]:
            d = appello["Data"]
            h = appello["orario_completo"]
            a = appello["Aula"]
            t = appello["TipoEsame"]
            row.append((d, h, a, t))

        for r in row:
            self.tree.insert("", tk.END, values=r)