    def iter_events(self, tag='', full=False, auto_reconnect=False):
        '''
        Creates a generator that continuously listens for events
        '''
        while True:
            data = self.get_event(tag=tag, full=full, auto_reconnect=auto_reconnect)
            if data is None:
                continue
            yield data