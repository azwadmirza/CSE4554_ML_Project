    def _walk(self, tree, topdown=True):
        dirs, nondirs = [], []
        for item in tree:
            name = _item_basename(item)
            if item.mode == GIT_MODE_DIR:
                dirs.append(name)
            else:
                nondirs.append(name)

        if topdown:
            yield os.path.normpath(tree.abspath), dirs, nondirs

        for i in dirs:
            yield from self._walk(tree[i], topdown=topdown)

        if not topdown:
            yield os.path.normpath(tree.abspath), dirs, nondirs