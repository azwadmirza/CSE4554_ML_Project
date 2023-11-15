    def call_parallel(self, cdata, low):
        '''
        Call the state defined in the given cdata in parallel
        '''
        # There are a number of possibilities to not have the cdata
        # populated with what we might have expected, so just be smart
        # enough to not raise another KeyError as the name is easily
        # guessable and fallback in all cases to present the real
        # exception to the user
        if len(cdata['args']) > 0:
            name = cdata['args'][0]
        elif 'name' in cdata['kwargs']:
            name = cdata['kwargs']['name']
        else:
            name = low.get('name', low.get('__id__'))

        proc = salt.utils.process.MultiprocessingProcess(
                target=self._call_parallel_target,
                args=(name, cdata, low))
        proc.start()
        ret = {'name': name,
                'result': None,
                'changes': {},
                'comment': 'Started in a separate process',
                'proc': proc}
        return ret