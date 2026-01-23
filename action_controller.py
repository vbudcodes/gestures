import time
import subprocess
from gesture_events import gesture_event_queue
import shared_state

STABILITY_TIME = 0.3
DEBOUNCE_TIME = 0.6

last_action = None
last_action_time = 0
stable_since = None
current_volume = 50

def set_volume(vol):
    vol = max(0, min(100, vol))
    script = f"set volume output volume {vol}"
    subprocess.call(["osascript", "-e", script])
    return vol

def toggle_mute():
    script = 'set volume output muted not (output muted of (get volume settings))'
    subprocess.call(["osascript", "-e", script])

def run():
    global last_action, last_action_time, stable_since, current_volume

    while True:
        event = gesture_event_queue.get()
        action = event["action"]
        now = time.time()

        if action != last_action:
            last_action = action
            stable_since = now
            continue

        if now - stable_since < STABILITY_TIME:
            continue

        if now - last_action_time < DEBOUNCE_TIME:
            continue

        if action == "UP":
            current_volume = set_volume(current_volume + 5)
        elif action == "DOWN":
            current_volume = set_volume(current_volume - 5)
        elif action == "MUTE":
            toggle_mute()

        shared_state.current_volume = current_volume
        shared_state.volume_changed_at = now
        last_action_time = now
