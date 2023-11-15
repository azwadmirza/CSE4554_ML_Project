    def file_list(self, tgt_env):
        '''
        Get file list for the target environment using GitPython
        '''
        files = set()
        symlinks = {}
        tree = self.get_tree(tgt_env)
        if not tree:
            # Not found, return empty objects
            return files, symlinks
        if self.root(tgt_env):
            try:
                tree = tree / self.root(tgt_env)
            except KeyError:
                return files, symlinks
            relpath = lambda path: os.path.relpath(path, self.root(tgt_env))
        else:
            relpath = lambda path: path
        add_mountpoint = lambda path: salt.utils.path.join(
            self.mountpoint(tgt_env), path, use_posixpath=True)
        for file_blob in tree.traverse():
            if not isinstance(file_blob, git.Blob):
                continue
            file_path = add_mountpoint(relpath(file_blob.path))
            files.add(file_path)
            if stat.S_ISLNK(file_blob.mode):
                stream = six.StringIO()
                file_blob.stream_data(stream)
                stream.seek(0)
                link_tgt = stream.read()
                stream.close()
                symlinks[file_path] = link_tgt
        return files, symlinks