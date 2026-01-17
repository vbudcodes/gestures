import cv2
import mediapipe as mp
import time
import math

# -------------------- MediaPipe Setup (INIT ONCE) --------------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# -------------------- Landmark Index Constants --------------------

TIP_IDS = [4, 8, 12, 16, 20]
PIP_IDS = [2, 6, 10, 14, 18]

# -------------------- FPS Tracking --------------------

_prev_time = 0

# -------------------- Helper Functions --------------------

def _distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def _is_thumb_up(lm):
    thumb_tip = lm[4]
    thumb_ip = lm[3]
    thumb_mcp = lm[2]
    wrist = lm[0]

    # Thumb pointing upward (y decreases upward)
    vertical = thumb_tip.y < thumb_ip.y < thumb_mcp.y

    # Thumb extended away from palm
    thumb_length = abs(thumb_tip.y - thumb_mcp.y)
    palm_size = abs(wrist.y - lm[9].y)

    extended = thumb_length > palm_size * 0.4

    return vertical and extended


def _other_fingers_folded(lm):
    folded = 0
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    for tip, pip in zip(tips, pips):
        if lm[tip].y > lm[pip].y:
            folded += 1

    return folded >= 3  # allow 1 noisy finger


def _detect_gesture(lm):
    # THUMBS UP (highest priority)
    if _is_thumb_up(lm) and _other_fingers_folded(lm):
        return "THUMBS_UP"

    # FIST
    folded = 0
    for tip, pip in zip([8,12,16,20], [6,10,14,18]):
        if lm[tip].y > lm[pip].y:
            folded += 1

    if folded == 4:
        return "FIST"

    # PALM
    extended = 0
    for tip, pip in zip([8,12,16,20], [6,10,14,18]):
        if lm[tip].y < lm[pip].y:
            extended += 1

    if extended == 4:
        return "PALM"

    return "UNKNOWN"



# Main Processing Function 

def process_frame(frame):
    global _prev_time

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    gesture = "NONE"

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        lm = hand_landmarks.landmark
        #fingers = _count_fingers(lm)
        gesture = _detect_gesture( lm)

    #  FPS Overlay 
    curr_time = time.time()
    fps = int(1 / (curr_time - _prev_time)) if _prev_time != 0 else 0
    _prev_time = curr_time

    cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"FPS: {fps}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    return frame, gesture
