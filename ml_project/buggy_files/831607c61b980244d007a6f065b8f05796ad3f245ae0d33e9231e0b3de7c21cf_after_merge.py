    def __init__(self, futures):
        super().__init__()
        for future in futures:
            future.add_done_callback(self.done_callback)