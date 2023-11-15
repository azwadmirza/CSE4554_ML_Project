    def _check_max_running(self, func, data, opts, now):
        '''
        Return the schedule data structure
        '''
        # Check to see if there are other jobs with this
        # signature running.  If there are more than maxrunning
        # jobs present then don't start another.
        # If jid_include is False for this job we can ignore all this
        # NOTE--jid_include defaults to True, thus if it is missing from the data
        # dict we treat it like it was there and is True

        # Check if we're able to run
        if not data['run']:
            return data
        if 'jid_include' not in data or data['jid_include']:
            jobcount = 0
            if self.opts['__role'] == 'master':
                current_jobs = salt.utils.master.get_running_jobs(self.opts)
            else:
                current_jobs = salt.utils.minion.running(self.opts)
            for job in current_jobs:
                if 'schedule' in job:
                    log.debug(
                        'schedule.handle_func: Checking job against fun '
                        '%s: %s', func, job
                    )
                    if data['name'] == job['schedule'] \
                            and salt.utils.process.os_is_running(job['pid']):
                        jobcount += 1
                        log.debug(
                            'schedule.handle_func: Incrementing jobcount, '
                            'now %s, maxrunning is %s',
                            jobcount, data['maxrunning']
                        )
                        if jobcount >= data['maxrunning']:
                            log.debug(
                                'schedule.handle_func: The scheduled job '
                                '%s was not started, %s already running',
                                data['name'], data['maxrunning']
                            )
                            data['_skip_reason'] = 'maxrunning'
                            data['_skipped'] = True
                            data['_skipped_time'] = now
                            data['run'] = False
                            return data
        return data