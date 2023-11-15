    def __init__(self, server):
        """
            server may be None if no server is needed.
        """
        self.server = server
        self.masterq = queue.Queue()
        self.should_exit = threading.Event()