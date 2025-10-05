from ui import Ui
from core import connected
from tkinter import messagebox

if __name__ == "__main__":
    if not connected():
        messagebox.showwarning("Error", "Connessione fallita! controlla stato internet/portale")
    else:
        Ui().mainloop()