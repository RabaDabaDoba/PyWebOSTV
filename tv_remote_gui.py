import os
import json
import customtkinter as ctk
from tkinter import messagebox
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl

TV_IP = "192.168.1.30"  # Replace with your TV's IP
STORE_PATH = "client_key.json"

# Connect to TV
if os.path.exists(STORE_PATH):
    with open(STORE_PATH, "r") as f:
        store = json.load(f)
else:
    store = {}

client = WebOSClient(TV_IP)
client.connect()
for status in client.register(store):
    if status == WebOSClient.PROMPTED:
        print("Accept the connection on the TV")
    elif status == WebOSClient.REGISTERED:
        print("Registered")

with open(STORE_PATH, "w") as f:
    json.dump(store, f)

media = MediaControl(client)

# Helper to sync ARC control
def sync_arc_audio():
    media.mute(True)
    media.mute(False)

# GUI setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("LG webOS ARC Media Remote")
app.geometry("500x380")

# Functions
def volume_up():
    sync_arc_audio()
    media.volume_up()

def volume_down():
    sync_arc_audio()
    media.volume_down()

def set_volume():
    try:
        val = int(volume_entry.get())
        if 0 <= val <= 100:
            sync_arc_audio()
            media.set_volume(val)
        else:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a number between 0 and 100.")

def get_volume():
    vol_info = media.get_volume()
    volume_status.configure(text=f"Volume: {vol_info['volume']} | Muted: {vol_info['muted']}")

def toggle_mute():
    status = mute_switch.get()
    media.mute(status)

def list_audio_outputs():
    global audio_output_list
    outputs = media.list_audio_output_sources()
    audio_output_list = outputs
    dropdown.configure(values=[o.name for o in outputs])

def set_audio_output(value):
    for o in audio_output_list:
        if o.name == value:
            media.set_audio_output(o)
            break

# UI
frame = ctk.CTkFrame(master=app)
frame.pack(padx=20, pady=20, fill="both", expand=True)

ctk.CTkLabel(frame, text="Volume Control", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

vol_buttons = ctk.CTkFrame(frame)
vol_buttons.pack(pady=5)

ctk.CTkButton(vol_buttons, text="Volume +", command=volume_up).grid(row=0, column=0, padx=5)
ctk.CTkButton(vol_buttons, text="Volume -", command=volume_down).grid(row=0, column=1, padx=5)

volume_entry = ctk.CTkEntry(frame, placeholder_text="0-100")
volume_entry.pack(pady=5)
ctk.CTkButton(frame, text="Set Volume", command=set_volume).pack()

ctk.CTkButton(frame, text="Get Volume", command=get_volume).pack(pady=5)
volume_status = ctk.CTkLabel(frame, text="Volume: ?")
volume_status.pack()

mute_switch = ctk.CTkSwitch(frame, text="Mute", command=toggle_mute)
mute_switch.pack(pady=10)

ctk.CTkLabel(frame, text="Playback", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
pb_frame = ctk.CTkFrame(frame)
pb_frame.pack(pady=5)
ctk.CTkButton(pb_frame, text="Play", command=media.play).grid(row=0, column=0, padx=5)
ctk.CTkButton(pb_frame, text="Pause", command=media.pause).grid(row=0, column=1, padx=5)
ctk.CTkButton(pb_frame, text="Stop", command=media.stop).grid(row=0, column=2, padx=5)
ctk.CTkButton(pb_frame, text="Rewind", command=media.rewind).grid(row=1, column=0, padx=5)
ctk.CTkButton(pb_frame, text="Fast Forward", command=media.fast_forward).grid(row=1, column=1, padx=5)

ctk.CTkLabel(frame, text="Audio Output", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
ctk.CTkButton(frame, text="Refresh Outputs", command=list_audio_outputs).pack()
dropdown = ctk.CTkOptionMenu(frame, values=[], command=set_audio_output)
dropdown.pack(pady=5)

app.mainloop()
