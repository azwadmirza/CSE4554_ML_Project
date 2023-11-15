    def __init__(self):
        self.event_queue = queue.Queue()
        self.should_exit = threading.Event()