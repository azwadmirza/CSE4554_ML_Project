    def __init__(self, message_queue: Queue = None) -> None:
        super(QueueOutputChannel).__init__()
        self.messages = Queue() if not message_queue else message_queue