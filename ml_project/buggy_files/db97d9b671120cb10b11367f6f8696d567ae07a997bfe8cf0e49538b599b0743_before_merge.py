    def issue_title(self):
        """Return the expected issue title for this logline."""
        result = self.traceback_lines[-1] if self.traceback_lines else self.message
        return result[:1000]