    def fromlineno(self):
        if self.lineno is None:
            return self._fixed_source_line()
        else:
            return self.lineno