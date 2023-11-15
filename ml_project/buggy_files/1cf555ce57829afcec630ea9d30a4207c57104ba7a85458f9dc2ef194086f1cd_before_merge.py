    def save_link(self, path_info):
        """Adds the specified path to the list of links created by dvc. This
        list is later used on `dvc checkout` to cleanup old links.

        Args:
            path_info (dict): path info to add to the list of links.
        """
        assert isinstance(path_info, str) or path_info.scheme == "local"

        if not os.path.exists(path_info):
            return

        mtime, _ = get_mtime_and_size(path_info, self.repo.tree)
        inode = get_inode(path_info)
        relative_path = relpath(path_info, self.root_dir)

        cmd = "REPLACE INTO {}(path, inode, mtime) " "VALUES (?, ?, ?)".format(
            self.LINK_STATE_TABLE
        )
        self._execute(cmd, (relative_path, self._to_sqlite(inode), mtime))