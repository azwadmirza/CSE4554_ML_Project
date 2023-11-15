    def set_pattern(self, pattern):
        """Set the pattern on the underlying model."""
        if not self.model():
            return
        self.pattern = pattern
        with debug.log_time(log.completion, 'Set pattern {}'.format(pattern)):
            self.model().set_pattern(pattern)
            self.selectionModel().clear()
            self._maybe_update_geometry()
            self._maybe_show()