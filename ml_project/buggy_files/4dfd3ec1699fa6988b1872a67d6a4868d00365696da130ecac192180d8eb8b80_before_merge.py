    def call_parallel(self, cdata, low):
        '''
        Call the state defined in the given cdata in parallel
        '''
        proc = salt.utils.process.MultiprocessingProcess(
                target=self._call_parallel_target,
                args=(cdata, low))
        proc.start()
        ret = {'name': cdata['args'][0],
                'result': None,
                'changes': {},
                'comment': 'Started in a separate process',
                'proc': proc}
        return ret