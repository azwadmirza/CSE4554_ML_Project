    def flush(self):
        """Flushes the file descriptor for the current thread."""
        return safe_flush(self.handle)