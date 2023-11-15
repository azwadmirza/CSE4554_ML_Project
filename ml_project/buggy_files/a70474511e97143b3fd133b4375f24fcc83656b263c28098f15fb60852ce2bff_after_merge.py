    def merge(self, other):
        """Combines two aggregator values."""
        self.last_update_timestamp = max(
            self.last_update_timestamp, other.last_update_timestamp
        )
        self.initial_checkpoint_timestamp = max(
            self.initial_checkpoint_timestamp,
            other.initial_checkpoint_timestamp,
        )