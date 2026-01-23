import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.prev_time = time.time()

    def _finger_count(self, landmarks, handedness):
        """
        Count fingers based on landmark positions.
        Works reliably for open/closed fingers.
        """
        tips = [4, 8, 12, 16, 20]
        pip = [2, 6, 10, 14, 18]

        count = 0

        # Thumb (different logic for left/right)
        if handedness == "Right":
            if landmarks[tips[0]].x < landmarks[pip[0]].x:
                count += 1
        else:
            if landmarks[tips[0]].x > landmarks[pip[0]].x:
                count += 1

        # Other 4 fingers
        for i in range(1, 5):
            if landmarks[tips[i]].y < landmarks[pip[i]].y:
                count += 1

        return count

    def _count_to_gesture(self, count):
        return {
            0: "FIST",
            1: "ONE",
            2: "TWO",
            3: "THREE",
            5: "PALM"
        }.get(count, None)

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        left_gesture = None
        right_gesture = None

        if results.multi_hand_landmarks and results.multi_handedness:
            for landmarks, handedness_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                handedness = handedness_info.classification[0].label
                count = self._finger_count(landmarks.landmark, handedness)
                gesture = self._count_to_gesture(count)

                if handedness == "Left":
                    left_gesture = gesture
                else:
                    right_gesture = gesture

                mp_drawing.draw_landmarks(
                    frame,
                    landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                cv2.putText(
                    frame,
                    f"{handedness}: {gesture}",
                    (int(landmarks.landmark[0].x * frame.shape[1]),
                     int(landmarks.landmark[0].y * frame.shape[0]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        # FPS
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        return frame, left_gesture, right_gesture
