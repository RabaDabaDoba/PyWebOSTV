# Full-featured LG TV Control Client (Step 2)
# GUI using customtkinter with multiple tabs and all PyWebOSTV controls

import os
import json
import threading
import customtkinter as ctk
from pywebostv.connection import WebOSClient
from pywebostv.controls import *

STORE_FILE = "client_store.json"


def load_store():
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_store(store):
    with open(STORE_FILE, "w") as f:
        json.dump(store, f)


class LGTVClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LG TV Control Client")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.client = None
        self.store = load_store()

        self.create_widgets()

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

        self.media_tab = self.tabview.add("Media")
        self.system_tab = self.tabview.add("System")
        self.app_tab = self.tabview.add("Apps")
        self.input_tab = self.tabview.add("Input")
        self.tv_tab = self.tabview.add("TV")
        self.source_tab = self.tabview.add("Source")

        self.create_connection_section()
        self.populate_media_tab()
        self.populate_system_tab()
        self.populate_app_tab()
        self.populate_input_tab()
        self.populate_tv_tab()
        self.populate_source_tab()

    def create_connection_section(self):
        self.ip_entry = ctk.CTkEntry(self, placeholder_text="Enter LG TV IP")
        self.ip_entry.pack(pady=5)
        self.connect_button = ctk.CTkButton(self, text="Connect", command=self.connect_tv)
        self.connect_button.pack(pady=5)
        self.status_label = ctk.CTkLabel(self, text="Not connected")
        self.status_label.pack(pady=5)

    def connect_tv(self):
        ip = self.ip_entry.get().strip()
        self.client = WebOSClient(ip)

        def do_connect():
            try:
                self.client.connect()
                for status in self.client.register(self.store):
                    if status == WebOSClient.REGISTERED:
                        save_store(self.store)
                        self.status_label.configure(text="Connected")
                        self.media = MediaControl(self.client)
                        self.system = SystemControl(self.client)
                        self.app = ApplicationControl(self.client)
                        self.input = InputControl(self.client)
                        self.tv_control = TvControl(self.client)
                        self.source = SourceControl(self.client)
            except Exception as e:
                self.status_label.configure(text=f"Error: {e}")

        threading.Thread(target=do_connect, daemon=True).start()

    def populate_media_tab(self):
        ctk.CTkButton(self.media_tab, text="Vol +", command=lambda: self.media.volume_up()).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Vol -", command=lambda: self.media.volume_down()).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Mute", command=lambda: self.media.mute(True)).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Unmute", command=lambda: self.media.mute(False)).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Play", command=self.media.play).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Pause", command=self.media.pause).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Stop", command=self.media.stop).pack(pady=2)

    def populate_system_tab(self):
        ctk.CTkButton(self.system_tab, text="Power Off", command=self.safe_call(self.system.power_off)).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Screen Off", command=self.safe_call(self.system.screen_off)).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Screen On", command=self.safe_call(self.system.screen_on)).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Notify", command=self.send_notification).pack(pady=2)

    def send_notification(self):
        try:
            self.system.notify("Hello from PC!")
        except Exception as e:
            self.status_label.configure(text=f"Notify error: {e}")

    def populate_app_tab(self):
        ctk.CTkButton(self.app_tab, text="List Apps", command=self.list_apps).pack(pady=2)
        self.app_output = ctk.CTkTextbox(self.app_tab, height=300)
        self.app_output.pack(pady=5, fill="both", expand=True)

    def list_apps(self):
        try:
            apps = self.app.list_apps()
            self.app_output.delete("0.0", "end")
            for a in apps:
                self.app_output.insert("end", f"{a['title']} - {a['id']}\n")
        except Exception as e:
            self.app_output.insert("end", f"Error: {e}\n")

    def populate_input_tab(self):
        ctk.CTkButton(self.input_tab, text="Up", command=self.safe_call(self.input.up)).pack(pady=2)
        ctk.CTkButton(self.input_tab, text="Down", command=self.safe_call(self.input.down)).pack(pady=2)
        ctk.CTkButton(self.input_tab, text="Left", command=self.safe_call(self.input.left)).pack(pady=2)
        ctk.CTkButton(self.input_tab, text="Right", command=self.safe_call(self.input.right)).pack(pady=2)
        ctk.CTkButton(self.input_tab, text="OK", command=self.safe_call(self.input.ok)).pack(pady=2)

    def populate_tv_tab(self):
        ctk.CTkButton(self.tv_tab, text="Channel +", command=self.safe_call(self.tv_control.channel_up)).pack(pady=2)
        ctk.CTkButton(self.tv_tab, text="Channel -", command=self.safe_call(self.tv_control.channel_down)).pack(pady=2)

    def populate_source_tab(self):
        ctk.CTkButton(self.source_tab, text="List Sources", command=self.list_sources).pack(pady=2)
        self.source_output = ctk.CTkTextbox(self.source_tab, height=200)
        self.source_output.pack(pady=5, fill="both", expand=True)

    def list_sources(self):
        try:
            sources = self.source.list_sources()
            self.source_output.delete("0.0", "end")
            for s in sources:
                self.source_output.insert("end", f"{s['label']}\n")
        except Exception as e:
            self.source_output.insert("end", f"Error: {e}\n")

    def safe_call(self, func):
        def wrapper():
            try:
                func()
            except Exception as e:
                self.status_label.configure(text=f"Error: {e}")
        return wrapper


if __name__ == "__main__":
    app = LGTVClient()
    app.mainloop()
