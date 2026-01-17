from queue import Queue

# Small size prevents backlog
gesture_queue = Queue(maxsize=5)
