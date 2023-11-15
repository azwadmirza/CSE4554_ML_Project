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