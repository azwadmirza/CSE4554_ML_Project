    def _prepare_save(self):
        """Prepare saving of the file.

        Return:
            True if the file should be saved, False otherwise.
        """
        if not os.path.exists(self._configdir):
            os.makedirs(self._configdir, 0o755)
        return True