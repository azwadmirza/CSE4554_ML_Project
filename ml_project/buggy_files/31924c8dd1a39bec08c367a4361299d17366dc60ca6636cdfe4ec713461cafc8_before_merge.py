    def event(self, chunk_ret):
        '''
        Fire an event on the master bus
        '''
        if not self.opts.get('local') and self.opts.get('state_events', True):
            tag = salt.utils.event.tagify([self.jid, chunk_ret['__run_num__']])
            self.functions['event.fire_master'](chunk_ret, tag)