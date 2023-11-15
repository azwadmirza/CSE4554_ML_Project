    def sendall(self, data):
        fileno = self.fileno()
        bytes_total = len(data)
        bytes_written = 0
        while True:
            try:
                bytes_written += _write(fileno, _get_memory(data, bytes_written))
            except (IOError, OSError) as ex:
                code = ex.args[0]
                if code not in ignored_errors:
                    raise
                sys.exc_clear()
            if bytes_written >= bytes_total:
                return
            self.hub.wait(self._write_event)