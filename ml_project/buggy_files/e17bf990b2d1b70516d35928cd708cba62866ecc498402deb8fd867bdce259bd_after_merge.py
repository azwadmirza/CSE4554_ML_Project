    def get_unused_links(self, used):
        """Removes all saved links except the ones that are used.

        Args:
            used (list): list of used links that should not be removed.
        """
        unused = []

        self._execute(f"SELECT * FROM {self.LINK_STATE_TABLE}")
        for row in self.cursor:
            relpath, inode, mtime = row
            inode = self._from_sqlite(inode)
            path = os.path.join(self.root_dir, relpath)

            if path in used or not os.path.exists(path):
                continue

            actual_inode = get_inode(path)
            actual_mtime, _ = get_mtime_and_size(path, self.tree)

            if (inode, mtime) == (actual_inode, actual_mtime):
                logger.debug("Removing '%s' as unused link.", path)
                unused.append(relpath)

        return unused