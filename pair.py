import os
import json
from pywebostv.connection import WebOSClient
from pywebostv.controls import *

STORE_PATH = "client_key.json"

# Load or initialize the store
if os.path.exists(STORE_PATH):
    with open(STORE_PATH, "r") as f:
        store = json.load(f)
else:
    store = {}

# Connect to your TV
client = WebOSClient("192.168.1.30")  # Replace with your TV IP
client.connect()

# Register the client with the TV
for status in client.register(store):
    if status == WebOSClient.PROMPTED:
        print("Please accept the connect on the TV!")
    elif status == WebOSClient.REGISTERED:
        print("Registration successful!")

# Save the token for future runs
with open(STORE_PATH, "w") as f:
    json.dump(store, f)

print("Stored key:", store)
