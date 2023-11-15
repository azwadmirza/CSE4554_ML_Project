    def dir_list(self, tgt_env):
        '''
        Get a list of directories for the target environment using pygit2
        '''
        def _traverse(tree, blobs, prefix):
            '''
            Traverse through a pygit2 Tree object recursively, accumulating all
            the empty directories within it in the "blobs" list
            '''
            for entry in iter(tree):
                blob = self.repo[entry.oid]
                if not isinstance(blob, pygit2.Tree):
                    continue
                blobs.append(os.path.join(prefix, entry.name))
                if len(blob):
                    _traverse(blob, blobs, os.path.join(prefix, entry.name))

        ret = set()
        tree = self.get_tree(tgt_env)
        if not tree:
            return ret
        if self.root:
            try:
                oid = tree[self.root].oid
                tree = self.repo[oid]
            except KeyError:
                return ret
            if not isinstance(tree, pygit2.Tree):
                return ret
            relpath = lambda path: os.path.relpath(path, self.root)
        else:
            relpath = lambda path: path
        blobs = []
        if len(tree):
            _traverse(tree, blobs, self.root)
        add_mountpoint = lambda path: os.path.join(self.mountpoint, path)
        for blob in blobs:
            ret.add(add_mountpoint(relpath(blob)))
        if self.mountpoint:
            ret.add(self.mountpoint)
        return ret