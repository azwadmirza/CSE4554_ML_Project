    def makedirs(self, path):
        self._sftp_connect()

        if self.isdir(path):
            return

        if self.isfile(path) or self.islink(path):
            raise DvcException(
                "a file with the same name '{}' already exists".format(path)
            )

        head, tail = posixpath.split(path)

        if head:
            self.makedirs(head)

        if tail:
            self._sftp.mkdir(path)