    def eval(self):
        '''
        Evaluate and execute the schedule
        '''
        schedule = self.option('schedule')
        #log.debug('calling eval {0}'.format(schedule))
        if not isinstance(schedule, dict):
            return
        if 'enabled' in schedule and not schedule['enabled']:
            return
        for job, data in schedule.items():
            if job == 'enabled':
                continue
            # Job is disabled, continue
            if 'enabled' in data and not data['enabled']:
                continue
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
                    'Invalid function: {0} in job {1}. Ignoring.'.format(
                        func, job
                    )
                )
                continue
            if 'name' not in data:
                data['name'] = job
            # Add up how many seconds between now and then
            when = 0
            seconds = 0

            time_conflict = False
            for item in ['seconds', 'minutes', 'hours', 'days']:
                if item in data and 'when' in data:
                    time_conflict = True

            if time_conflict:
                log.info('Unable to use "seconds", "minutes", "hours", or "days" with "when" option.  Ignoring.')
                continue

            # clean this up
            if 'seconds' in data or 'minutes' in data or 'hours' in data or 'days' in data:
                # Add up how many seconds between now and then
                seconds += int(data.get('seconds', 0))
                seconds += int(data.get('minutes', 0)) * 60
                seconds += int(data.get('hours', 0)) * 3600
                seconds += int(data.get('days', 0)) * 86400
            elif 'when' in data:
                if not _WHEN_SUPPORTED:
                    log.info('Missing python-dateutil.  Ignoring job {0}'.format(job))
                    continue

                if isinstance(data['when'], list):
                    _when = []
                    now = int(time.time())
                    for i in data['when']:
                        try:
                            tmp = int(dateutil_parser.parse(i).strftime('%s'))
                        except ValueError:
                            log.info('Invalid date string {0}.  Ignoring job {1}.'.format(i, job))
                            continue
                        if tmp >= now:
                            _when.append(tmp)
                    _when.sort()
                    if _when:
                        # Grab the first element
                        # which is the next run time
                        when = _when[0]

                        # If we're switching to the next run in a list
                        # ensure the job can run
                        if '_when' in data and data['_when'] != when:
                            data['_when_run'] = True
                            data['_when'] = when
                        seconds = when - int(time.time())

                        # scheduled time is in the past
                        if seconds < 0:
                            continue

                        if '_when_run' not in data:
                            data['_when_run'] = True

                        # Backup the run time
                        if '_when' not in data:
                            data['_when'] = when

                        # A new 'when' ensure _when_run is True
                        if when > data['_when']:
                            data['_when'] = when
                            data['_when_run'] = True

                    else:
                        continue

                else:
                    try:
                        when = int(dateutil_parser.parse(data['when']).strftime('%s'))
                    except ValueError:
                        log.info('Invalid date string.  Ignoring')
                        continue

                    now = int(time.time())
                    seconds = when - now

                    # scheduled time is in the past
                    if seconds < 0:
                        continue

                    if '_when_run' not in data:
                        data['_when_run'] = True

                    # Backup the run time
                    if '_when' not in data:
                        data['_when'] = when

                    # A new 'when' ensure _when_run is True
                    if when > data['_when']:
                        data['_when'] = when
                        data['_when_run'] = True

            else:
                continue
            # Check if the seconds variable is lower than current lowest
            # loop interval needed. If it is lower then overwrite variable
            # external loops using can then check this variable for how often
            # they need to reschedule themselves
            if seconds < self.loop_interval:
                self.loop_interval = seconds
            now = int(time.time())
            run = False
            if job in self.intervals:
                if 'when' in data:
                    if now - when >= seconds:
                        if data['_when_run']:
                            data['_when_run'] = False
                            run = True
                else:
                    if now - self.intervals[job] >= seconds:
                        run = True

            else:
                if 'splay' in data:
                    if 'when' in data:
                        log.debug('Unable to use "splay" with "when" option at this time.  Ignoring.')
                    else:
                        data['_seconds'] = data['seconds']

                if 'when' in data:
                    if now - when >= seconds:
                        if data['_when_run']:
                            data['_when_run'] = False
                            run = True
                else:
                    run = True

            if run:
                if 'range' in data:
                    if not _RANGE_SUPPORTED:
                        log.info('Missing python-dateutil.  Ignoring job {0}'.format(job))
                        continue
                    else:
                        if isinstance(data['range'], dict):
                            try:
                                start = int(dateutil_parser.parse(data['range']['start']).strftime('%s'))
                            except ValueError:
                                log.info('Invalid date string for start.  Ignoring job {0}.'.format(job))
                                continue
                            try:
                                end = int(dateutil_parser.parse(data['range']['end']).strftime('%s'))
                            except ValueError:
                                log.info('Invalid date string for end.  Ignoring job {0}.'.format(job))
                                continue
                            if end > start:
                                if 'invert' in data['range'] and data['range']['invert']:
                                    if now <= start or now >= end:
                                        run = True
                                    else:
                                        run = False
                                else:
                                    if now >= start and now <= end:
                                        run = True
                                    else:
                                        run = False
                            else:
                                log.info('schedule.handle_func: Invalid range, end must be larger than start. \
                                         Ignoring job {0}.'.format(job))
                                continue
                        else:
                            log.info('schedule.handle_func: Invalid, range must be specified as a dictionary. \
                                     Ignoring job {-1}.'.format(job))
                            continue

            if not run:
                continue
            else:
                if 'splay' in data:
                    if 'when' in data:
                        log.debug('Unable to use "splay" with "when" option at this time.  Ignoring.')
                    else:
                        if isinstance(data['splay'], dict):
                            if data['splay']['end'] > data['splay']['start']:
                                splay = random.randint(data['splay']['start'], data['splay']['end'])
                            else:
                                log.info('schedule.handle_func: Invalid Splay, end must be larger than start. \
                                         Ignoring splay.')
                                splay = None
                        else:
                            splay = random.randint(0, data['splay'])

                        if splay:
                            log.debug('schedule.handle_func: Adding splay of '
                                      '{0} seconds to next run.'.format(splay))
                            data['seconds'] = data['_seconds'] + splay

                log.debug('Running scheduled job: {0}'.format(job))

            if 'jid_include' not in data or data['jid_include']:
                data['jid_include'] = True
                log.debug('schedule: This job was scheduled with jid_include, '
                          'adding to cache (jid_include defaults to True)')
                if 'maxrunning' in data:
                    log.debug('schedule: This job was scheduled with a max '
                              'number of {0}'.format(data['maxrunning']))
                else:
                    log.info('schedule: maxrunning parameter was not specified for '
                             'job {0}, defaulting to 1.'.format(job))
                    data['maxrunning'] = 1

            try:
                if self.opts.get('multiprocessing', True):
                    thread_cls = multiprocessing.Process
                else:
                    thread_cls = threading.Thread
                proc = thread_cls(target=self.handle_func, args=(func, data))
                proc.start()
                if self.opts.get('multiprocessing', True):
                    proc.join()
            finally:
                self.intervals[job] = int(time.time())