    def open(self, path, binary=False):

        relpath = os.path.relpath(path, self.git.working_dir)

        obj = self.git_object_by_path(path)
        if obj is None:
            msg = "No such file in branch '{}'".format(self.rev)
            raise IOError(errno.ENOENT, msg, relpath)
        if obj.mode == GIT_MODE_DIR:
            raise IOError(errno.EISDIR, "Is a directory", relpath)

        # GitPython's obj.data_stream is a fragile thing, it is better to
        # read it immediately, also it needs to be to decoded if we follow
        # the `open()` behavior (since data_stream.read() returns bytes,
        # and `open` with default "r" mode returns str)
        data = obj.data_stream.read()
        if binary:
            return BytesIO(data)
        return StringIO(data.decode("utf-8"))