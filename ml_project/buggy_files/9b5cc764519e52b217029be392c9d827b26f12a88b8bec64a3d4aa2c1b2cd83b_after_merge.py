    def close(self):
        '''
        Cleanly shutdown the router socket
        '''
        if self._closing:
            return
        self._closing = True
        if hasattr(self, '_monitor') and self._monitor is not None:
            self._monitor.stop()
            self._monitor = None
        if hasattr(self, '_w_monitor') and self._w_monitor is not None:
            self._w_monitor.stop()
            self._w_monitor = None
        if hasattr(self, 'clients'):
            self.clients.close()
        self.stream.close()