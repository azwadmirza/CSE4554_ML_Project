    def save(self, path_info, checksum):
        """Save checksum for the specified path info.

        Args:
            path_info (dict): path_info to save checksum for.
            checksum (str): checksum to save.
        """
        assert isinstance(path_info, str) or path_info.scheme == "local"
        assert checksum is not None
        assert os.path.exists(path_info)

        actual_mtime, actual_size = get_mtime_and_size(path_info, self.tree)
        actual_inode = get_inode(path_info)

        existing_record = self.get_state_record_for_inode(actual_inode)
        if not existing_record:
            self._insert_new_state_record(
                actual_inode, actual_mtime, actual_size, checksum
            )
            return

        self._update_state_for_path_changed(
            actual_inode, actual_mtime, actual_size, checksum
        )