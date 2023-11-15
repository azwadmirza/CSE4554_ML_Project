    def destroy(self):
        if hasattr(self, '_monitor') and self._monitor is not None:
            self._monitor.stop()
            self._monitor = None
        if hasattr(self, '_stream'):
            self._stream.close(0)
        elif hasattr(self, '_socket'):
            self._socket.close(0)
        if hasattr(self, 'context') and self.context.closed is False:
            self.context.term()