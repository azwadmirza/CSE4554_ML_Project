    def commit(self):
        """Remove temporary save dir: rollback will no longer be possible."""
        self.save_dir.cleanup()
        self._moved_paths = []