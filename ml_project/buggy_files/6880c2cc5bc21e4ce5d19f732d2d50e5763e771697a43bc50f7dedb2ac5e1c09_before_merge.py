    def _check_files(self):
        """Check the existence of mandatory files for a given distribution."""
        for fname in self.MANDATORY_FILES:
            if self._metadata_dir_full_path:
                fpath = join(self._metadata_dir_full_path, fname)
                assert isfile(fpath)