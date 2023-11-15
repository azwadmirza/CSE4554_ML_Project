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
        if hasattr(self, 'clients') and self.clients.closed is False:
            self.clients.close()
        if hasattr(self, 'workers') and self.workers.closed is False:
            self.workers.close()
        if hasattr(self, 'stream'):
            self.stream.close()
        if hasattr(self, 'context') and self.context.closed is False:
            self.context.term()