    def clear_socket(self):
        '''
        delete socket if you have it
        '''
        if hasattr(self, '_socket'):
            if isinstance(self.poller.sockets, dict):
                for socket in self.poller.sockets.keys():
                    self.poller.unregister(socket)
            else:
                for socket in self.poller.sockets:
                    self.poller.unregister(socket[0])
            del self._socket