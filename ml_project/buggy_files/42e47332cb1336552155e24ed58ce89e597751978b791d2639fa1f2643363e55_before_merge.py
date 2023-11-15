    def get_event(self, wait=0.25, tag='', full=False):
        '''
        Returns next available event with tag tag from event bus
        If any within wait seconds
        Otherwise return None

        If tag is empty then return events for all tags
        If full then add tag field to returned data

        If wait is 0 then block forever or until next event becomes available.
        '''
        return (self.event.get_event(wait=wait, tag=tag, full=full))