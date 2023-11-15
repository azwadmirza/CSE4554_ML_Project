    def __repr__(self):
        return '<%s at 0x%x %s_fobj=%r%s>' % (
            self.__class__.__name__,
            id(self),
            'closed' if self.closed else '',
            self.io,
            self._extra_repr()
        )