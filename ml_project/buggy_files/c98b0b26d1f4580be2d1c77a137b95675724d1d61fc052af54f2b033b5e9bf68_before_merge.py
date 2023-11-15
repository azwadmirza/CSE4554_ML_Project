    def get(self, path_info):
        """Gets the checksum for the specified path info. Checksum will be
        retrieved from the state database if available.

        Args:
            path_info (dict): path info to get the checksum for.

        Returns:
            str or None: checksum for the specified path info or None if it
            doesn't exist in the state database.
        """
        assert isinstance(path_info, str) or path_info.scheme == "local"
        path = os.fspath(path_info)

        if not os.path.exists(path):
            return None

        actual_mtime, actual_size = get_mtime_and_size(path, self.repo.tree)
        actual_inode = get_inode(path)

        existing_record = self.get_state_record_for_inode(actual_inode)
        if not existing_record:
            return None

        mtime, size, checksum, _ = existing_record
        if self._file_metadata_changed(actual_mtime, mtime, actual_size, size):
            return None

        self._update_state_record_timestamp_for_inode(actual_inode)
        return checksum