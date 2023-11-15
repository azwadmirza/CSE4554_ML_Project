    def file_list(self, tgt_env):
        '''
        Get file list for the target environment using pygit2
        '''
        def _traverse(tree, blobs, prefix):
            '''
            Traverse through a pygit2 Tree object recursively, accumulating all
            the file paths and symlink info in the "blobs" dict
            '''
            for entry in iter(tree):
                if entry.oid not in self.repo:
                    # Entry is a submodule, skip it
                    continue
                obj = self.repo[entry.oid]
                if isinstance(obj, pygit2.Blob):
                    repo_path = os.path.join(prefix, entry.name)
                    blobs.setdefault('files', []).append(repo_path)
                    if stat.S_ISLNK(tree[entry.name].filemode):
                        link_tgt = self.repo[tree[entry.name].oid].data
                        blobs.setdefault('symlinks', {})[repo_path] = link_tgt
                elif isinstance(obj, pygit2.Tree):
                    _traverse(obj, blobs, os.path.join(prefix, entry.name))

        files = set()
        symlinks = {}
        tree = self.get_tree(tgt_env)
        if not tree:
            # Not found, return empty objects
            return files, symlinks
        if self.root:
            try:
                # This might need to be changed to account for a root that
                # spans more than one directory
                oid = tree[self.root].oid
                tree = self.repo[oid]
            except KeyError:
                return files, symlinks
            if not isinstance(tree, pygit2.Tree):
                return files, symlinks
            relpath = lambda path: os.path.relpath(path, self.root)
        else:
            relpath = lambda path: path
        blobs = {}
        if len(tree):
            _traverse(tree, blobs, self.root)
        add_mountpoint = lambda path: os.path.join(self.mountpoint, path)
        for repo_path in blobs.get('files', []):
            files.add(add_mountpoint(relpath(repo_path)))
        for repo_path, link_tgt in six.iteritems(blobs.get('symlinks', {})):
            symlinks[add_mountpoint(relpath(repo_path))] = link_tgt
        return files, symlinks