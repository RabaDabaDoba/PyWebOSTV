import json
from pywebostv.connection import WebOSClient
from pywebostv.controls import *
import customtkinter as ctk
import requests
from PIL import Image, ImageTk, UnidentifiedImageError
import io

class LGTVClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LG TV Client")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.client = None
        self.media = None
        self.app_control = None
        self.system = None
        self.input = None
        self.tv = None
        self.source = None

        self.create_widgets()
        self.after(100, self.connect_to_tv)

    def load_store(self):
        try:
            with open("client_store.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_store(self, store):
        with open("client_store.json", "w") as f:
            json.dump(store, f)

    def connect_to_tv(self):
        try:
            ip_address = "192.168.1.30"  # Replace with your actual TV IP
            self.client = WebOSClient(ip_address)
            store = self.load_store()
            self.client.connect()
            for status in self.client.register(store):
                if status == WebOSClient.PROMPTED:
                    print("Please accept the connection on the TV.")
                elif status == WebOSClient.REGISTERED:
                    print("Registered successfully.")
            self.save_store(store)

            self.media = MediaControl(self.client)
            self.app_control = ApplicationControl(self.client)
            self.system = SystemControl(self.client)
            self.input = InputControl(self.client)
            self.tv = TvControl(self.client)
            self.source = SourceControl(self.client)

            self.create_tabs()

        except Exception as e:
            ctk.CTkLabel(self, text=f"Connection failed: {e}").pack(pady=10)

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both")

    def create_tabs(self):
        self.media_tab = self.tabview.add("Media")
        self.app_tab = self.tabview.add("Apps")
        self.system_tab = self.tabview.add("System")

        self.populate_media_tab()
        self.populate_app_tab()
        self.populate_system_tab()

    def populate_media_tab(self):
        ctk.CTkButton(self.media_tab, text="Volume Up", command=self.media.volume_up).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Volume Down", command=self.media.volume_down).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Mute", command=lambda: self.media.mute(True)).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Unmute", command=lambda: self.media.mute(False)).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Play", command=self.media.play).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Pause", command=self.media.pause).pack(pady=2)
        ctk.CTkButton(self.media_tab, text="Stop", command=self.media.stop).pack(pady=2)

    def populate_app_tab(self):
        apps = self.app_control.list_apps()
                                                  # foreground app.
        foreground_app = [x for x in apps if app_id == x["id"]][0]
                                                        # Application app["id"] == app.data["id"].
        icon_url = foreground_app["icon"]   
        print(icon_url)
            
    def populate_system_tab(self):
        ctk.CTkButton(self.system_tab, text="Power Off", command=self.system.power_off).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Screen Off", command=self.system.screen_off).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Screen On", command=self.system.screen_on).pack(pady=2)

if __name__ == "__main__":
    app = LGTVClient()
    app.mainloop()