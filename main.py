import cv2
from hand_tracking import process_frame
from gesture_events import gesture_queue

import threading
from action_controller import action_worker

threading.Thread(target=action_worker, daemon=True).start()


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, gesture = process_frame(frame)

        # Push gesture event (non-blocking)
        if gesture != "NONE" and not gesture_queue.full():
            gesture_queue.put(gesture)

        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
