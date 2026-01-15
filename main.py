import cv2
from hand_tracking import process_frame
from action_controller import ActionController

controller = ActionController()

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame, gesture = process_frame(frame)
    controller.perform_action(gesture)

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
