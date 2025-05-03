import cv2
import mediapipe as mp
import numpy as np
from pywebostv.connection import WebOSClient
from pywebostv.controls import InputControl

# Connect to the TV
client = WebOSClient("192.168.1.30")  # Replace with your TV's IP address
client.connect()
for status in client.register({"client_key": "4dcf5256e1286ad433d10c2f9a04ae2d"}):  # Replace or obtain client_key
    print(status)

inp = InputControl(client)
try:
    inp.connect_input()
except Exception as e:
    print("Failed to connect to input:", e)
    exit()

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)
screen_w, screen_h = 1920, 1080  # You can adjust this to your TV resolution or desired scale
prev_x, prev_y = 0, 0
click_state = False

def calc_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    img_h, img_w, _ = img.shape

    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0].landmark
        index_finger = lm[8]   # Tip of index finger
        thumb = lm[4]          # Tip of thumb

        # Normalize position
        x = screen_w - int(index_finger.x * screen_w)
        y = int(index_finger.y * screen_h)

        # Move if change is large enough
        dx = x - prev_x
        dy = y - prev_y
        if abs(dx) > 5 or abs(dy) > 5:
            inp.move(dx, dy)
            prev_x, prev_y = x, y

        # Check for pinch gesture (click)
        pinch_dist = calc_distance((index_finger.x, index_finger.y), (thumb.x, thumb.y))
        if pinch_dist < 0.05:
            if not click_state:
                inp.click()
                click_state = True
        else:
            click_state = False

        # Visualize
        mp_draw.draw_landmarks(img, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
inp.disconnect_input()
