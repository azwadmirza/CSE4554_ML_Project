    def run_job(self, name):
        '''
        Run a schedule job now
        '''
        data = self._get_schedule().get(name, {})

        if 'function' in data:
            func = data['function']
        elif 'func' in data:
            func = data['func']
        elif 'fun' in data:
            func = data['fun']
        else:
            func = None
        if func not in self.functions:
            log.info(
                'Invalid function: %s in scheduled job %s.',
                func, name
            )

        if 'name' not in data:
            data['name'] = name

        # Assume run should be True until we check max_running
        if 'run' not in data:
            data['run'] = True

        if not self.standalone:
            data = self._check_max_running(func,
                                           data,
                                           self.opts,
                                           datetime.datetime.now())

        # Grab run, assume True
        if data.get('run'):
            log.info('Running Job: %s', name)
            self._run_job(func, data)