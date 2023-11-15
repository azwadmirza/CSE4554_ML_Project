    def check_failhard(self, low, running):
        '''
        Check if the low data chunk should send a failhard signal
        '''
        tag = _gen_tag(low)
        if self.opts.get('test', False):
            return False
        if (low.get('failhard', False) or self.opts['failhard']) and tag in running:
            if running[tag]['result'] is None:
                return False
            return not running[tag]['result']
        return False