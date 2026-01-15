import time

class ActionController:
    def __init__(self):
        self.last_action_time = 0
        self.delay = 0.5  # debounce delay in seconds

    def can_perform_action(self):
        current_time = time.time()
        if current_time - self.last_action_time > self.delay:
            self.last_action_time = current_time
            return True
        return False

    def perform_action(self, gesture_name):
        """
        This method will later map gestures to system actions.
        Currently acts as a placeholder.
        """
        if not self.can_perform_action():
            return

        if gesture_name == "VOLUME_UP":
            print("Volume Up Gesture Detected")

        elif gesture_name == "VOLUME_DOWN":
            print("Volume Down Gesture Detected")

        elif gesture_name == "MUTE":
            print("Mute Gesture Detected")
