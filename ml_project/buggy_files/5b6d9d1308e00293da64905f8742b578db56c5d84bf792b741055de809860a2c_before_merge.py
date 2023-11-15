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
        log.info('Running Job: %s', name)

        if not self.standalone:
            data = self._check_max_running(func,
                                           data,
                                           self.opts,
                                           datetime.datetime.now())

        # Grab run, assume True
        run = data.get('run', True)
        if run:
            self._run_job(func, data)