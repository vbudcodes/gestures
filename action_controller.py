import time
import subprocess
from collections import deque
from gesture_events import gesture_queue

DEBOUNCE_TIME = 0.8
STABILITY_FRAMES = 4  

gesture_buffer = deque(maxlen=STABILITY_FRAMES)
_last_action_time = 0
_last_confirmed_gesture = None

# Volume Helpers 

def get_volume():
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True,
        text=True
    )
    return int(result.stdout.strip())

def set_volume(value):
    value = max(0, min(100, value))
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {value}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def mute_volume():
    subprocess.run(
        ["osascript", "-e", "set volume with output muted"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def unmute_volume():
    subprocess.run(
        ["osascript", "-e", "set volume without output muted"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

#  Gesture → Action

def perform_action(gesture):
    current = get_volume()

    if gesture == "THUMBS_UP":
        set_volume(current + 10)

    elif gesture == "FIST":
        set_volume(current - 10)

    elif gesture == "PALM":
        mute_volume()

#worker

def action_worker():
    global _last_action_time, _last_confirmed_gesture

    while True:
        gesture = gesture_queue.get()
        gesture_buffer.append(gesture)

        # Require stable gesture
        if len(gesture_buffer) < STABILITY_FRAMES:
            continue

        if not all(g == gesture for g in gesture_buffer):
            continue

        now = time.time()

        if gesture == _last_confirmed_gesture:
            continue

        if now - _last_action_time < DEBOUNCE_TIME:
            continue

        perform_action(gesture)

        _last_action_time = now
        _last_confirmed_gesture = gesture
