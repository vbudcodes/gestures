from queue import Queue

# Small queue to avoid backlog
gesture_event_queue = Queue(maxsize=5)
