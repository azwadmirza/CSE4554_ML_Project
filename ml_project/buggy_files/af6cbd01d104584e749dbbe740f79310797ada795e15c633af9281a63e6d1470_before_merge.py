    def destroy(self):
        if hasattr(self, '_monitor') and self._monitor is not None:
            self._monitor.stop()
            self._monitor = None
        if hasattr(self, '_stream'):
            # TODO: Optionally call stream.close() on newer pyzmq? Its broken on some
            self._stream.io_loop.remove_handler(self._stream.socket)
            self._stream.socket.close(0)
        elif hasattr(self, '_socket'):
            self._socket.close(0)
        if hasattr(self, 'context') and self.context.closed is False:
            self.context.term()