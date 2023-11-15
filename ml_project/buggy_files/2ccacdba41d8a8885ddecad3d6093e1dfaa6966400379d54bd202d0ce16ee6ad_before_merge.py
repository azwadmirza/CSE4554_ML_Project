    def update_remote_filepath(self):
        # if the file string is different in the iofile, update the remote object
        # (as in the case of wildcard expansion)
        remote_object = self.remote_object
        if remote_object._file != self._file:
            remote_object._iofile = self