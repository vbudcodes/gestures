# 🖐️ Hand Gesture Volume Control

Control your Mac's system volume hands-free — using only a webcam and hand gestures.

Built with Python, OpenCV, and MediaPipe. No ML training. No extra hardware.

---

## Why I Built This

Started as a simple curiosity — could I control my laptop volume without touching the keyboard?

The first version worked, but barely. The OpenCV window would freeze on volume changes, FPS would drop, and gestures felt sluggish. The issue wasn't the detection — it was everything being crammed into a single loop, with system calls blocking the camera feed.

The fix was pulling the volume control into a separate thread with a queue in between. One architectural change, and the whole thing became smooth and reliable.

This project ended up teaching me less about gestures and more about building systems that actually hold up in real time.

---

## Gesture Map

The system uses both hands. The left hand sets the mode, the right hand acts. This prevents accidental triggers.

**Left hand — Mode**

| Gesture | Mode |
|---------|------|
| Open palm (5 fingers) | Volume Control |
| Fist (0 fingers) | *(Reserved)* |

**Right hand — Action (Volume Mode)**

| Gesture | Action |
|---------|--------|
| 1 finger | Volume Up (+5%) |
| 2 fingers | Mute / Unmute |
| 3 fingers | Volume Down (-5%) |

If no left hand is detected, nothing happens.

---

## Architecture

Gesture detection and system actions run in separate threads, connected by a queue.

```
┌──────────────────────────────┐
│         Camera Loop          │
│   OpenCV + MediaPipe         │
│                              │
│  Detects gestures            │
│  → pushes to Queue           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Action Controller       │
│      (Daemon Thread)         │
│                              │
│  Reads Queue                 │
│  → runs AppleScript          │
└──────────────────────────────┘
```

The camera loop never blocks. FPS stays stable regardless of what the action thread is doing.

---

## Project Structure

```
gesture-volume-control/
├── main.py               # Camera loop, gesture resolution, UI overlay
├── hand_tracking.py      # MediaPipe setup, landmark detection, finger counting
├── action_controller.py  # Daemon thread — volume control via AppleScript
├── gesture_events.py     # Shared queue between threads
├── shared_state.py       # Shared UI state (volume level, timestamp)
├── requirements.txt
└── README.md
```

---

## Getting Started

**Requirements:** macOS · Python 3.7+ · Webcam

```bash
git clone https://github.com/your-username/gesture-volume-control.git
cd gesture-volume-control
pip install -r requirements.txt
python main.py
```

Press `Q` to quit.

---

## Tech Stack

| Tool | Role |
|------|------|
| OpenCV | Webcam capture and frame rendering |
| MediaPipe | 21-point hand landmark detection |
| NumPy | Coordinate calculations |
| AppleScript | macOS system volume control |
| threading + Queue | Decoupled event architecture |

---

## What I Learned

- Blocking calls inside real-time loops kill performance — always offload them
- Queues and daemon threads are a clean, simple solution for this kind of separation
- Stability comes from architecture, not just better code inside the loop
- Real-world gesture recognition needs debouncing and stability windows to feel usable

---

## Platform Note

Volume control uses AppleScript and is **macOS only**. The detection and camera logic is cross-platform — only `action_controller.py` would need adapting for Windows or Linux.

---

*Built by [vbudcodes](https://github.com/your-vbudcodes)*