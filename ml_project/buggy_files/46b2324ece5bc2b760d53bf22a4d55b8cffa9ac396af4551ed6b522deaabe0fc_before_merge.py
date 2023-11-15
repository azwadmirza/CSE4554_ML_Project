    def eval(self):
        '''
        Evaluate and execute the schedule
        '''

        def _splay(splaytime):
            '''
            Calculate splaytime
            '''
            splay_ = None
            if isinstance(splaytime, dict):
                if splaytime['end'] >= splaytime['start']:
                    splay_ = random.randint(splaytime['start'],
                                            splaytime['end'])
                else:
                    log.error('schedule.handle_func: Invalid Splay, '
                              'end must be larger than start. Ignoring splay.')
            else:
                splay_ = random.randint(1, splaytime)
            return splay_

        schedule = self._get_schedule()
        if not isinstance(schedule, dict):
            raise ValueError('Schedule must be of type dict.')
        if 'enabled' in schedule and not schedule['enabled']:
            return
        for job, data in six.iteritems(schedule):
            if job == 'enabled' or not data:
                continue
            if not isinstance(data, dict):
                log.error('Scheduled job "{0}" should have a dict value, not {1}'.format(job, type(data)))
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
                    'Invalid function: {0} in scheduled job {1}.'.format(
                        func, job
                    )
                )
            if 'name' not in data:
                data['name'] = job

            if '_next_fire_time' not in data:
                data['_next_fire_time'] = None

            if '_splay' not in data:
                data['_splay'] = None

            if 'run_on_start' in data and \
                    data['run_on_start'] and \
                    '_run_on_start' not in data:
                data['_run_on_start'] = True

            now = int(time.time())

            if 'until' in data:
                if not _WHEN_SUPPORTED:
                    log.error('Missing python-dateutil. '
                              'Ignoring until.')
                else:
                    until__ = dateutil_parser.parse(data['until'])
                    until = int(time.mktime(until__.timetuple()))

                    if until <= now:
                        log.debug('Until time has passed '
                                  'skipping job: {0}.'.format(data['name']))
                        continue

            if 'after' in data:
                if not _WHEN_SUPPORTED:
                    log.error('Missing python-dateutil. '
                              'Ignoring after.')
                else:
                    after__ = dateutil_parser.parse(data['after'])
                    after = int(time.mktime(after__.timetuple()))

                    if after >= now:
                        log.debug('After time has not passed '
                                  'skipping job: {0}.'.format(data['name']))
                        continue

            # Used for quick lookups when detecting invalid option combinations.
            schedule_keys = set(data.keys())

            time_elements = ('seconds', 'minutes', 'hours', 'days')
            scheduling_elements = ('when', 'cron', 'once')

            invalid_sched_combos = [set(i)
                    for i in itertools.combinations(scheduling_elements, 2)]

            if any(i <= schedule_keys for i in invalid_sched_combos):
                log.error('Unable to use "{0}" options together. Ignoring.'
                          .format('", "'.join(scheduling_elements)))
                continue

            invalid_time_combos = []
            for item in scheduling_elements:
                all_items = itertools.chain([item], time_elements)
                invalid_time_combos.append(
                    set(itertools.combinations(all_items, 2)))

            if any(set(x) <= schedule_keys for x in invalid_time_combos):
                log.error('Unable to use "{0}" with "{1}" options. Ignoring'
                          .format('", "'.join(time_elements),
                                  '", "'.join(scheduling_elements)))
                continue

            if True in [True for item in time_elements if item in data]:
                if '_seconds' not in data:
                    interval = int(data.get('seconds', 0))
                    interval += int(data.get('minutes', 0)) * 60
                    interval += int(data.get('hours', 0)) * 3600
                    interval += int(data.get('days', 0)) * 86400

                    data['_seconds'] = interval

                    if not data['_next_fire_time']:
                        data['_next_fire_time'] = now + data['_seconds']

                    if interval < self.loop_interval:
                        self.loop_interval = interval

            elif 'once' in data:
                if data['_next_fire_time'] and \
                        data['_next_fire_time'] != now and \
                        not data['_splay']:
                    continue

                if not data['_next_fire_time'] and \
                        not data['_splay']:
                    once_fmt = data.get('once_fmt', '%Y-%m-%dT%H:%M:%S')
                    try:
                        once = datetime.datetime.strptime(data['once'],
                                                          once_fmt)
                        data['_next_fire_time'] = int(
                            time.mktime(once.timetuple()))
                    except (TypeError, ValueError):
                        log.error('Date string could not be parsed: %s, %s',
                                  data['once'], once_fmt)
                        continue
                    if data['_next_fire_time'] != now:
                        continue

            elif 'when' in data:
                if not _WHEN_SUPPORTED:
                    log.error('Missing python-dateutil. '
                              'Ignoring job {0}.'.format(job))
                    continue

                if isinstance(data['when'], list):
                    _when = []
                    for i in data['when']:
                        if ('pillar' in self.opts and 'whens' in self.opts['pillar'] and
                                i in self.opts['pillar']['whens']):
                            if not isinstance(self.opts['pillar']['whens'],
                                              dict):
                                log.error('Pillar item "whens" must be dict. '
                                          'Ignoring')
                                continue
                            __when = self.opts['pillar']['whens'][i]
                            try:
                                when__ = dateutil_parser.parse(__when)
                            except ValueError:
                                log.error('Invalid date string. Ignoring')
                                continue
                        elif ('whens' in self.opts['grains'] and
                              i in self.opts['grains']['whens']):
                            if not isinstance(self.opts['grains']['whens'],
                                              dict):
                                log.error('Grain "whens" must be dict.'
                                          'Ignoring')
                                continue
                            __when = self.opts['grains']['whens'][i]
                            try:
                                when__ = dateutil_parser.parse(__when)
                            except ValueError:
                                log.error('Invalid date string. Ignoring')
                                continue
                        else:
                            try:
                                when__ = dateutil_parser.parse(i)
                            except ValueError:
                                log.error('Invalid date string {0}. '
                                          'Ignoring job {1}.'.format(i, job))
                                continue
                        _when.append(int(time.mktime(when__.timetuple())))

                    if data['_splay']:
                        _when.append(data['_splay'])

                    # Sort the list of "whens" from earlier to later schedules
                    _when.sort()

                    # Copy the list so we can loop through it
                    for i in copy.deepcopy(_when):
                        if i < now and len(_when) > 1:
                            # Remove all missed schedules except the latest one.
                            # We need it to detect if it was triggered previously.
                            _when.remove(i)

                    if _when:
                        # Grab the first element, which is the next run time or
                        # last scheduled time in the past.
                        when = _when[0]

                        if '_run' not in data:
                            # Prevent run of jobs from the past
                            data['_run'] = bool(when >= now)

                        if not data['_next_fire_time']:
                            data['_next_fire_time'] = when

                        if data['_next_fire_time'] < when and \
                                not data['_run']:
                            data['_next_fire_time'] = when
                            data['_run'] = True

                    elif not data.get('_run', False):
                        data['_next_fire_time'] = None
                        continue

                else:
                    if ('pillar' in self.opts and 'whens' in self.opts['pillar'] and
                            data['when'] in self.opts['pillar']['whens']):
                        if not isinstance(self.opts['pillar']['whens'], dict):
                            log.error('Pillar item "whens" must be dict.'
                                      'Ignoring')
                            continue
                        _when = self.opts['pillar']['whens'][data['when']]
                        try:
                            when__ = dateutil_parser.parse(_when)
                        except ValueError:
                            log.error('Invalid date string. Ignoring')
                            continue
                    elif ('whens' in self.opts['grains'] and
                          data['when'] in self.opts['grains']['whens']):
                        if not isinstance(self.opts['grains']['whens'], dict):
                            log.error('Grain "whens" must be dict. Ignoring')
                            continue
                        _when = self.opts['grains']['whens'][data['when']]
                        try:
                            when__ = dateutil_parser.parse(_when)
                        except ValueError:
                            log.error('Invalid date string. Ignoring')
                            continue
                    else:
                        try:
                            when__ = dateutil_parser.parse(data['when'])
                        except ValueError:
                            log.error('Invalid date string. Ignoring')
                            continue
                    when = int(time.mktime(when__.timetuple()))

                    if when < now and \
                            not data.get('_run', False) and \
                            not data['_splay']:
                        data['_next_fire_time'] = None
                        continue

                    if '_run' not in data:
                        data['_run'] = True

                    if not data['_next_fire_time']:
                        data['_next_fire_time'] = when

                    if data['_next_fire_time'] < when and \
                            not data['_run']:
                        data['_next_fire_time'] = when
                        data['_run'] = True

            elif 'cron' in data:
                if not _CRON_SUPPORTED:
                    log.error('Missing python-croniter. Ignoring job {0}'.format(job))
                    continue

                if data['_next_fire_time'] is None:
                    # Get next time frame for a "cron" job if it has been never
                    # executed before or already executed in the past.
                    try:
                        data['_next_fire_time'] = int(
                            croniter.croniter(data['cron'], now).get_next())
                    except (ValueError, KeyError):
                        log.error('Invalid cron string. Ignoring')
                        continue

                    # If next job run is scheduled more than 1 minute ahead and
                    # configured loop interval is longer than that, we should
                    # shorten it to get our job executed closer to the beginning
                    # of desired time.
                    interval = now - data['_next_fire_time']
                    if interval >= 60 and interval < self.loop_interval:
                        self.loop_interval = interval

            else:
                continue

            run = False
            seconds = data['_next_fire_time'] - now

            if 'splay' in data:
                # Got "splay" configured, make decision to run a job based on that
                if not data['_splay']:
                    # Try to add "splay" time only if next job fire time is
                    # still in the future. We should trigger job run
                    # immediately otherwise.
                    splay = _splay(data['splay'])
                    if now < data['_next_fire_time'] + splay:
                        log.debug('schedule.handle_func: Adding splay of '
                                  '{0} seconds to next run.'.format(splay))
                        data['_splay'] = data['_next_fire_time'] + splay
                        if 'when' in data:
                            data['_run'] = True
                    else:
                        run = True

                if data['_splay']:
                    # The "splay" configuration has been already processed, just use it
                    seconds = data['_splay'] - now

            if seconds <= 0:
                if '_seconds' in data:
                    run = True
                elif 'when' in data and data['_run']:
                    data['_run'] = False
                    run = True
                elif 'cron' in data:
                    # Reset next scheduled time because it is in the past now,
                    # and we should trigger the job run, then wait for the next one.
                    data['_next_fire_time'] = None
                    run = True
                elif seconds == 0:
                    run = True

            if '_run_on_start' in data and data['_run_on_start']:
                run = True
                data['_run_on_start'] = False
            elif run:
                if 'range' in data:
                    if not _RANGE_SUPPORTED:
                        log.error('Missing python-dateutil. Ignoring job {0}'.format(job))
                        continue
                    else:
                        if isinstance(data['range'], dict):
                            try:
                                start = int(time.mktime(dateutil_parser.parse(data['range']['start']).timetuple()))
                            except ValueError:
                                log.error('Invalid date string for start. Ignoring job {0}.'.format(job))
                                continue
                            try:
                                end = int(time.mktime(dateutil_parser.parse(data['range']['end']).timetuple()))
                            except ValueError:
                                log.error('Invalid date string for end. Ignoring job {0}.'.format(job))
                                continue
                            if end > start:
                                if 'invert' in data['range'] and data['range']['invert']:
                                    if now <= start or now >= end:
                                        run = True
                                    else:
                                        run = False
                                else:
                                    if start <= now <= end:
                                        run = True
                                    else:
                                        run = False
                            else:
                                log.error('schedule.handle_func: Invalid range, end must be larger than start. \
                                         Ignoring job {0}.'.format(job))
                                continue
                        else:
                            log.error('schedule.handle_func: Invalid, range must be specified as a dictionary. \
                                     Ignoring job {0}.'.format(job))
                            continue

            if not run:
                continue

            miss_msg = ''
            if seconds < 0:
                miss_msg = ' (runtime missed ' \
                           'by {0} seconds)'.format(abs(seconds))

            log.info('Running scheduled job: {0}{1}'.format(job, miss_msg))

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

            multiprocessing_enabled = self.opts.get('multiprocessing', True)

            if salt.utils.is_windows():
                # Temporarily stash our function references.
                # You can't pickle function references, and pickling is
                # required when spawning new processes on Windows.
                functions = self.functions
                self.functions = {}
                returners = self.returners
                self.returners = {}
            try:
                if multiprocessing_enabled:
                    thread_cls = SignalHandlingMultiprocessingProcess
                else:
                    thread_cls = threading.Thread
                proc = thread_cls(target=self.handle_func, args=(multiprocessing_enabled, func, data))

                if multiprocessing_enabled:
                    with default_signals(signal.SIGINT, signal.SIGTERM):
                        # Reset current signals before starting the process in
                        # order not to inherit the current signal handlers
                        proc.start()
                else:
                    proc.start()

                if multiprocessing_enabled:
                    proc.join()
            finally:
                if '_seconds' in data:
                    data['_next_fire_time'] = now + data['_seconds']
                data['_splay'] = None
            if salt.utils.is_windows():
                # Restore our function references.
                self.functions = functions
                self.returners = returners