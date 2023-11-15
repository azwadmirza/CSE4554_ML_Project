    def tolineno(self):
        if not self._astroid_fields:
            # can't have children
            lastchild = None
        else:
            lastchild = self.last_child()
        if lastchild is None:
            return self.fromlineno
        else:
            return lastchild.tolineno

        # TODO / FIXME:
        assert self.fromlineno is not None, self
        assert self.tolineno is not None, self