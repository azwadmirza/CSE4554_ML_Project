    def makedirs(self, path):
        self._sftp_connect()

        # Single stat call will say whether this is a dir, a file or a link
        st_mode = self.st_mode(path)

        if stat.S_ISDIR(st_mode):
            return

        if stat.S_ISREG(st_mode) or stat.S_ISLNK(st_mode):
            raise DvcException(
                "a file with the same name '{}' already exists".format(path)
            )

        head, tail = posixpath.split(path)

        if head:
            self.makedirs(head)

        if tail:
            try:
                self._sftp.mkdir(path)
            except IOError as e:
                # Since paramiko errors are very vague we need to recheck
                # whether it's because path already exists or something else
                if e.errno == errno.EACCES or not self.exists(path):
                    raise