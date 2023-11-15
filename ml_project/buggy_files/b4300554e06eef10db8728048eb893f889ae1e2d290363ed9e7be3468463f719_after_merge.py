    def save_link(self, path_info):
        """Adds the specified path to the list of links created by dvc. This
        list is later used on `dvc checkout` to cleanup old links.

        Args:
            path_info (dict): path info to add to the list of links.
        """
        assert path_info.scheme == "local"
        path = fspath_py35(path_info)

        if not os.path.exists(path):
            return

        mtime, _ = get_mtime_and_size(path)
        inode = get_inode(path)
        relative_path = relpath(path, self.root_dir)

        cmd = (
            "REPLACE INTO {}(path, inode, mtime) "
            'VALUES ("{}", {}, "{}")'.format(
                self.LINK_STATE_TABLE,
                relative_path,
                self._to_sqlite(inode),
                mtime,
            )
        )
        self._execute(cmd)