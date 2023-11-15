    def _walk(self, tree, topdown=True):
        dirs, nondirs = [], []
        for i in _iter_tree(tree):
            if i.mode == GIT_MODE_DIR:
                dirs.append(i.name)
            else:
                nondirs.append(i.name)

        if topdown:
            yield os.path.normpath(tree.abspath), dirs, nondirs

        for i in dirs:
            yield from self._walk(tree[i], topdown=topdown)

        if not topdown:
            yield os.path.normpath(tree.abspath), dirs, nondirs