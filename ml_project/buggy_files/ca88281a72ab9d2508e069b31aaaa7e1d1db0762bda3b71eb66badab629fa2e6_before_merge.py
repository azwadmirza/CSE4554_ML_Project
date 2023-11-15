    def clear_socket(self):
        '''
        delete socket if you have it
        '''
        if hasattr(self, '_socket'):
            if self._socket in self.poller:
                self.poller.unregister(self._socket)
            del self._socket