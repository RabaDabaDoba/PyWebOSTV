import os
import json
import customtkinter as ctk
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl

STORE_FILE = "client_store.json"


def load_store():
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_store(store):
    with open(STORE_FILE, "w") as f:
        json.dump(store, f)


class PairingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pair with LG TV")
        self.geometry("400x200")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.store = load_store()
        self.client = None

        self.label = ctk.CTkLabel(self, text="Enter LG TV IP Address:")
        self.label.pack(pady=10)

        self.ip_entry = ctk.CTkEntry(self, placeholder_text="192.168.1.30")
        self.ip_entry.pack(pady=5)

        self.status = ctk.CTkLabel(self, text="")
        self.status.pack()

        self.button = ctk.CTkButton(self, text="Connect and Pair", command=self.pair)
        self.button.pack(pady=20)

    def pair(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            self.status.configure(text="Please enter a valid IP address.")
            return

        self.client = WebOSClient(ip)
        try:
            self.client.connect()
        except Exception as e:
            self.status.configure(text=f"Connection failed: {e}")
            return

        for status in self.client.register(self.store):
            if status == WebOSClient.PROMPTED:
                self.status.configure(text="Please accept pairing on the TV...")
            elif status == WebOSClient.REGISTERED:
                self.status.configure(text="✅ Paired successfully!")
                save_store(self.store)
                self.after(1500, self.destroy)  # Close window after success


if __name__ == "__main__":
    app = PairingApp()
    app.mainloop()
