    def update(self, value):
        """Updates the current with the new value."""
        if self.checkpointed:
            self.initial_checkpoint_timestamp = time_ns()
            self.checkpointed = False
        self.last_update_timestamp = time_ns()