    def get_event(self, wait=0.25, tag='', full=False):
        '''
        Get a single salt event.
        If no events are available, then block for up to ``wait`` seconds.
        Return the event if it matches the tag (or ``tag`` is empty)
        Otherwise return None

        If wait is 0 then block forever or until next event becomes available.
        '''
        return (self.event.get_event(wait=wait, tag=tag, full=full))