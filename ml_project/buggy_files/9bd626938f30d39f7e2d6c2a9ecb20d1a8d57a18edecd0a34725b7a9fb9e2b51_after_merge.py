    def __init__(self, config=None):
        self._lock = threading.Lock()
        self.last_update_timestamp = 0
        self.initial_checkpoint_timestamp = 0
        self.checkpointed = True
        if config is not None:
            self.config = config
        else:
            self.config = {}