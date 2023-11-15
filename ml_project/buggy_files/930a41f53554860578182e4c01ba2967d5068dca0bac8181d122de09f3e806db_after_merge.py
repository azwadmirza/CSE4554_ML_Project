        def _send(self, data):
            if self.child_fd is None:
                return None

            if not select.select([], [self.child_fd], [], 0)[1]:
                return 0

            try:
                if self.stdin_logger:
                    self.stdin_logger.log(self.stdin_logger_level, data)
                if six.PY3:
                    written = os.write(self.child_fd, data.encode(__salt_system_encoding__))
                else:
                    written = os.write(self.child_fd, data)
            except OSError as why:
                if why.errno == errno.EPIPE:  # broken pipe
                    os.close(self.child_fd)
                    self.child_fd = None
                    return
                raise
            return written