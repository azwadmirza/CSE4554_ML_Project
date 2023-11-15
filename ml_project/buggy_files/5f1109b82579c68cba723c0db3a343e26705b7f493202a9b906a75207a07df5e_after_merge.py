    def _receive(self):
        c = self.subclient
        ret = []
        try:
            ret.append(self._receive_one(c))
        except Empty:
            pass
        while c.connection is not None and c.connection.can_read(timeout=0):
            ret.append(self._receive_one(c))
        return any(ret)