    def __init__(self, message_queue: Queue = None) -> None:
        self.messages = Queue() if not message_queue else message_queue