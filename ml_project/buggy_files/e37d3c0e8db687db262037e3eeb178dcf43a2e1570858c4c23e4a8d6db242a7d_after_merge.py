    def _walk(
        self,
        tree,
        topdown=True,
        ignore_file_handler=None,
        dvc_ignore_filter=None,
    ):
        dirs, nondirs = [], []
        for i in tree:
            if i.mode == GIT_MODE_DIR:
                dirs.append(i.name)
            else:
                nondirs.append(i.name)

        if topdown:
            if not dvc_ignore_filter:
                dvc_ignore_filter = DvcIgnoreFilter(
                    tree.abspath, ignore_file_handler=ignore_file_handler
                )
            dirs, nondirs = dvc_ignore_filter(tree.path, dirs, nondirs)
            yield os.path.normpath(tree.abspath), dirs, nondirs

        for i in dirs:
            for x in self._walk(
                tree[i],
                topdown=True,
                ignore_file_handler=ignore_file_handler,
                dvc_ignore_filter=dvc_ignore_filter,
            ):
                yield x

        if not topdown:
            yield os.path.normpath(tree.abspath), dirs, nondirs