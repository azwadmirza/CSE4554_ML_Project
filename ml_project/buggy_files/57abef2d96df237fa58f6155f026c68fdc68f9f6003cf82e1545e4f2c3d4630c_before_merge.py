    def take_checkpoint(self):
        """Stores a snapshot of the current value."""
        self.last_checkpoint_timestamp = time_ns()