import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


def is_thumb_open(hand_landmarks):
    return hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x


def count_fingers(hand_landmarks):
    count = 0

    if is_thumb_open(hand_landmarks):
        count += 1

    fingers = [
        (8, 6),    # Index
        (12, 10),  # Middle
        (16, 14),  # Ring
        (20, 18)   # Pinky
    ]

    for tip, joint in fingers:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
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

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            gesture = detect_gesture(hand_landmarks)

            cv2.putText(
                frame,
                f"Gesture: {gesture}",
                (50, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    cv2.imshow("Hand Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
