import cv2
import time
from hand_tracking import HandTracker
from gesture_events import gesture_event_queue
import shared_state
import threading
import action_controller

def resolve_mode_and_action(left, right):
    if left == "PALM":
        mode = "VOLUME"
    elif left == "FIST":
        mode = "SYSTEM"
    else:
        return None, None

    if mode == "VOLUME":
        if right == "ONE":
            return mode, "UP"
        elif right == "THREE":
            return mode, "DOWN"
        elif right == "TWO":
            return mode, "MUTE"

    return None, None


def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    action_thread = threading.Thread(
        target=action_controller.run,
        daemon=True
    )
    action_thread.start()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # mirror camera for display


        frame, left_gesture, right_gesture = tracker.process_frame(frame)
        mode, action = resolve_mode_and_action(left_gesture, right_gesture)

        if mode and action:
            try:
                gesture_event_queue.put_nowait({
                    "mode": mode,
                    "action": action
                })
            except:
                pass

        # UI Overlay
        if mode:
            cv2.putText(
                frame,
                f"MODE: {mode}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

        if action:
            cv2.putText(
                frame,
                f"ACTION: {action}",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 200, 200),
                2
            )

        # Volume bar display
        if (
            shared_state.current_volume is not None
            and time.time() - shared_state.volume_changed_at < 1.0
        ):
            vol = shared_state.current_volume
            cv2.rectangle(frame, (10, 140), (10 + vol * 2, 170), (0, 255, 0), -1)
            cv2.rectangle(frame, (10, 140), (210, 170), (255, 255, 255), 2)
            cv2.putText(frame, f"{vol}%", (220, 165),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
