    def _prepare_save(self):
        """Prepare saving of the file.

        Return:
            True if the file should be saved, False otherwise.
        """
        os.makedirs(self._configdir, 0o755, exist_ok=True)
        return True