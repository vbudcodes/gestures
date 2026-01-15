import cv2
import mediapipe as mp
from collections import deque

#mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,   # allow two hands
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# Gesture smoothing buffer
gesture_history = deque(maxlen=10)

# Small tolerance to avoid flickering
THRESHOLD = 0.02


def is_thumb_open(hand_landmarks):
    # Thumb moves sideways (x-axis)
    return hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x


def count_fingers(hand_landmarks):
    count = 0

    # Thumb
    if is_thumb_open(hand_landmarks):
        count += 1

    # Other fingers
    fingers = [
        (8, 6),    # Index
        (12, 10),  # Middle
        (16, 14),  # Ring
        (20, 18)   # Pinky
    ]

    for tip, joint in fingers:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y - THRESHOLD:
            count += 1

    return count


def detect_gesture(hand_landmarks):
    finger_count = count_fingers(hand_landmarks)
    thumb_open = is_thumb_open(hand_landmarks)

    if finger_count == 0:
        return "FIST"

    if finger_count == 5:
        return "PALM"

    if thumb_open and finger_count == 1:
        return "THUMBS UP"

    return "UNKNOWN"


# Start webcam

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # Draw landmarks
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Raw gesture (single frame)
            raw_gesture = detect_gesture(hand_landmarks)
            gesture_history.append(raw_gesture)

            # Smoothed gesture (most common in recent frames)
            gesture = max(set(gesture_history), key=gesture_history.count)

            # Place text near wrist
            wrist = hand_landmarks.landmark[0]
            h, w, _ = frame.shape
            x, y = int(wrist.x * w), int(wrist.y * h)

            cv2.putText(
                frame,
                gesture,
                (x - 30, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    cv2.imshow("Hand Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
def process_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = "NONE"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            raw_gesture = detect_gesture(hand_landmarks)
            gesture_history.append(raw_gesture)
            gesture = max(set(gesture_history), key=gesture_history.count)

    return frame, gesture
