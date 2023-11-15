    def issue_title(self):
        """Return the expected issue title for this logline."""
        if self.traceback_lines:
            result = next((line for line in reversed(self.traceback_lines) if line.strip()), self.message)
        else:
            result = self.message
        return result[:1000]