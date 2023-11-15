    def __init__(self, trainer):
        self.trainer = trainer
        self.early_stopping_accumulator = None
        self.checkpoint_accumulator = None
        self.accumulated_loss = None
        self.warning_cache = WarningCache()
        self._teardown_already_run = False
        self.running_loss = TensorRunningAccum(window_length=20)