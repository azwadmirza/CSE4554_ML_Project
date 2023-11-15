    def flush(self):
        """Flushes the file descriptor for the current thread."""
        return self.handle.flush()