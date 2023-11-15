    def unlisten(self):
        ''' Stop listening on ports. The server will no longer be usable after
        calling this function.

        Returns:
            None

        '''
        yield self._http.close_all_connections()
        self._http.stop()