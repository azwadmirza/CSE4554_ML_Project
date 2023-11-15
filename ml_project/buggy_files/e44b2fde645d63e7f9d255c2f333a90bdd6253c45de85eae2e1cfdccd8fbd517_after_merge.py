    def git_object_by_path(self, path):
        import git

        path = relpath(os.path.realpath(path), self.git.working_dir)
        assert path.split(os.sep, 1)[0] != ".."

        self._try_fetch_from_remote()

        try:
            tree = self.git.tree(self.rev)
        except git.exc.BadName as exc:
            raise DvcException(
                "revision '{}' not found in git '{}'".format(
                    self.rev, os.path.relpath(self.git.working_dir)
                ),
                cause=exc,
            )

        if not path or path == ".":
            return tree
        for i in path.split(os.sep):
            if not self._is_tree_and_contains(tree, i):
                # there is no tree for specified path
                return None
            tree = tree[i]
        return tree