import json
from pywebostv.connection import WebOSClient
from pywebostv.controls import SystemControl

with open("client_key.json", "r") as f:
    store = json.load(f)

client = WebOSClient("192.168.1.30")  # Your TV's IP
client.connect()
client.register(store)

system = SystemControl(client)
system.power_off()
