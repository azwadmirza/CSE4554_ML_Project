    def process_unix(self, file, family, inodes, filter_pid=None):
        """Parse /proc/net/unix files."""
        with open_text(file, buffering=BIGGER_FILE_BUFFERING) as f:
            f.readline()  # skip the first line
            for line in f:
                tokens = line.split()
                try:
                    _, _, _, _, type_, _, inode = tokens[0:7]
                except ValueError:
                    raise RuntimeError(
                        "error while parsing %s; malformed line %r" % (
                            file, line))
                if inode in inodes:
                    # With UNIX sockets we can have a single inode
                    # referencing many file descriptors.
                    pairs = inodes[inode]
                else:
                    pairs = [(None, -1)]
                for pid, fd in pairs:
                    if filter_pid is not None and filter_pid != pid:
                        continue
                    else:
                        if len(tokens) == 8:
                            path = tokens[-1]
                        else:
                            path = ""
                        type_ = int(type_)
                        raddr = None
                        status = _common.CONN_NONE
                        yield (fd, family, type_, path, raddr, status, pid)