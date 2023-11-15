    def save_history(self):
        """Save the directory in the history for incremental imports.
        """
        if self.is_album and not self.sentinel:
            history_add(self.paths)