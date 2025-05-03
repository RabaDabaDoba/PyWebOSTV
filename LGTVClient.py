import json
from pywebostv.connection import WebOSClient
from pywebostv.controls import *
import customtkinter as ctk
import requests
from PIL import Image, ImageTk, UnidentifiedImageError
import io
from os import remove
from urllib.request import urlretrieve



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
        self.custom = 1
        self.create_widgets()
        self.after(100, self.connect_to_tv)

    def on_closing():
        print("closing")

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
            ip_address = "192.168.1.14"  # Replace with your actual TV IP
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
        self.pointer_tab = ctk.CTkTabview(self.tabview)
        self.tabview.add("Pointer")
        
        


    def create_tabs(self):
        self.media_tab = self.tabview.add("Media")
        self.app_tab = self.tabview.add("Apps")
        self.system_tab = self.tabview.add("System")
        self.pointer_tab = self.tabview.tab("Pointer")

        self.populate_media_tab()
        self.populate_app_tab()
        self.populate_system_tab()
        self.populate_pointer_tab()

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

        # Create scrollable frame if you have many apps
        scrollable_frame = ctk.CTkScrollableFrame(self.app_tab, label_text="Available Apps")
        scrollable_frame.pack(expand=True, fill="both", padx=10, pady=10)

        for app in apps:
            app_title = app.data.get("title", app.data.get("id", "Unknown App"))
            
            def launch(app_ref=app, title=app_title):
                try:
                    self.app_control.launch(app_ref)
                    print(f"Launched: {title}")
                except Exception as e:
                    print(f"Failed to launch {title}: {e}")

            ctk.CTkButton(scrollable_frame, text=app_title, command=launch).pack(pady=4, padx=5, fill="x")

    def populate_system_tab(self):
        ctk.CTkButton(self.system_tab, text="Power Off", command=self.system.power_off).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Screen Off", command=self.system.screen_off).pack(pady=2)
        ctk.CTkButton(self.system_tab, text="Screen On", command=self.system.screen_on).pack(pady=2)


    def populate_pointer_tab(self):
        self.pointer_input = InputControl(self.client)

        self.pointer_tab.columnconfigure(0, weight=1)
        self.pointer_tab.rowconfigure(1, weight=1)

        connect_button = ctk.CTkButton(self.pointer_tab, text="Connect Pointer Control", command=self.connect_pointer)
        connect_button.grid(row=0, column=0, pady=(10, 5), padx=10)

        touchpad = ctk.CTkCanvas(self.pointer_tab, width=300, height=200, bg="#222222", highlightthickness=1, highlightbackground="#555")
        touchpad.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
        touchpad.bind("<ButtonPress-1>", self.start_drag)
        touchpad.bind("<B1-Motion>", self.do_drag)
        touchpad.bind("<ButtonRelease-1>", self.end_drag)

        click_button = ctk.CTkButton(self.pointer_tab, text="Click", command=self.click_pointer)
        click_button.grid(row=2, column=0, pady=(5, 10), padx=10)

        self.last_x = None
        self.last_y = None

    def connect_pointer(self):
        try:
            if self.client is None:
                print("TV not connected yet.")
                return

            self.pointer_input = InputControl(self.client)
            self.pointer_input.connect_input()
            print("Pointer control connected.")
        except Exception as e:
            print(f"Failed to connect pointer control: {e}")


    def start_drag(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def do_drag(self, event):
        if self.last_x is not None and self.last_y is not None:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            try:
                self.pointer_input.move(dx, dy)
            except Exception as e:
                print(f"Pointer move failed: {e}")
            self.last_x = event.x
            self.last_y = event.y

    def end_drag(self, event):
        self.last_x = None
        self.last_y = None

    def click_pointer(self):
        try:
            self.pointer_input.click()
        except Exception as e:
            print(f"Pointer click failed: {e}")


if __name__ == "__main__":
    app = LGTVClient()
    app.mainloop()