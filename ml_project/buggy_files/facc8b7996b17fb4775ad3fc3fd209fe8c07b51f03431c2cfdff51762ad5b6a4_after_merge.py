    def commit(self):
        """Remove temporary save dir: rollback will no longer be possible."""
        for save_dir in self._save_dirs:
            save_dir.cleanup()
        self._moved_paths = []