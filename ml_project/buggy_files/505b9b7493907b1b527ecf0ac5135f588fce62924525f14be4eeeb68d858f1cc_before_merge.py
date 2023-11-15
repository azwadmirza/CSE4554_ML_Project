    def get_event(self, wait=5, tag='', match_type=None, full=False, no_block=None):
        '''
        Get a single publication.
        IF no publication available THEN block for up to wait seconds
        AND either return publication OR None IF no publication available.

        IF wait is 0 then block forever.
        '''
        if not self.connected:
            self.connect_pub()
        start = time.time()
        while True:
            self.stack.serviceAll()
            if self.stack.rxMsgs:
                msg, sender = self.stack.rxMsgs.popleft()
                if 'tag' not in msg and 'data' not in msg:
                    # Invalid event, how did this get here?
                    continue
                if not msg['tag'].startswith(tag):
                    # Not what we are looking for, throw it away
                    continue
                if full:
                    return msg
                else:
                    return msg['data']
            if start + wait < time.time():
                return None
            time.sleep(0.01)