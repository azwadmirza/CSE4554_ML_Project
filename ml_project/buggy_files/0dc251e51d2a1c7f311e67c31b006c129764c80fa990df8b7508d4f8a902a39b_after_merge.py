    def find_file(self, path, tgt_env):
        '''
        Find the specified file in the specified environment
        '''
        tree = self.get_tree(tgt_env)
        if not tree:
            # Branch/tag/SHA not found in repo
            return None, None, None
        blob = None
        depth = 0
        while True:
            depth += 1
            if depth > SYMLINK_RECURSE_DEPTH:
                blob = None
                break
            try:
                file_blob = tree / path
                if stat.S_ISLNK(file_blob.mode):
                    # Path is a symlink. The blob data corresponding to
                    # this path's object ID will be the target of the
                    # symlink. Follow the symlink and set path to the
                    # location indicated in the blob data.
                    stream = six.BytesIO()
                    file_blob.stream_data(stream)
                    stream.seek(0)
                    link_tgt = salt.utils.stringutils.to_str(stream.read())
                    stream.close()
                    path = salt.utils.path.join(
                        os.path.dirname(path), link_tgt, use_posixpath=True)
                else:
                    blob = file_blob
                    if isinstance(blob, git.Tree):
                        # Path is a directory, not a file.
                        blob = None
                    break
            except KeyError:
                # File not found or repo_path points to a directory
                blob = None
                break
        if isinstance(blob, git.Blob):
            return blob, blob.hexsha, blob.mode
        return None, None, None