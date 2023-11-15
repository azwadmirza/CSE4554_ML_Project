    def eval(self, now=None):
        '''
        Evaluate and execute the schedule

        :param datetime now: Override current time with a datetime object instance``

        '''

        log.trace('==== evaluating schedule now %s =====', now)

        loop_interval = self.opts['loop_interval']
        if not isinstance(loop_interval, datetime.timedelta):
            loop_interval = datetime.timedelta(seconds=loop_interval)

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
        if 'skip_function' in schedule:
            self.skip_function = schedule['skip_function']
        if 'skip_during_range' in schedule:
            self.skip_during_range = schedule['skip_during_range']

        _hidden = ['enabled',
                   'skip_function',
                   'skip_during_range']
        for job, data in six.iteritems(schedule):

            # Clear out _skip_reason from previous runs
            if '_skip_reason' in data:
                del data['_skip_reason']

            run = False

            if job in _hidden:
                continue

            if not isinstance(data, dict):
                log.error(
                    'Scheduled job "%s" should have a dict value, not %s',
                    job, type(data)
                )
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
                    'Invalid function: %s in scheduled job %s.',
                    func, job
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

            if not now:
                now = datetime.datetime.now()

            # Used for quick lookups when detecting invalid option combinations.
            schedule_keys = set(data.keys())

            time_elements = ('seconds', 'minutes', 'hours', 'days')
            scheduling_elements = ('when', 'cron', 'once')

            invalid_sched_combos = [set(i)
                    for i in itertools.combinations(scheduling_elements, 2)]

            if any(i <= schedule_keys for i in invalid_sched_combos):
                log.error(
                    'Unable to use "%s" options together. Ignoring.',
                    '", "'.join(scheduling_elements)
                )
                continue

            invalid_time_combos = []
            for item in scheduling_elements:
                all_items = itertools.chain([item], time_elements)
                invalid_time_combos.append(
                    set(itertools.combinations(all_items, 2)))

            if any(set(x) <= schedule_keys for x in invalid_time_combos):
                log.error(
                    'Unable to use "%s" with "%s" options. Ignoring',
                    '", "'.join(time_elements),
                    '", "'.join(scheduling_elements)
                )
                continue

            if 'run_explicit' in data:
                _run_explicit = []
                for _run_time in data['run_explicit']:
                    if isinstance(_run_time, datetime.datetime):
                        _run_explicit.append(_run_time)
                    else:
                        _run_explicit.append(datetime.datetime.strptime(_run_time['time'],
                                                                        _run_time['time_fmt']))

                # Copy the list so we can loop through it
                for i in copy.deepcopy(_run_explicit):
                    if len(_run_explicit) > 1:
                        if i < now - loop_interval:
                            _run_explicit.remove(i)

                if _run_explicit:
                    if _run_explicit[0] <= now < _run_explicit[0] + loop_interval:
                        run = True
                        data['_next_fire_time'] = _run_explicit[0]

            if True in [True for item in time_elements if item in data]:
                if '_seconds' not in data:
                    interval = int(data.get('seconds', 0))
                    interval += int(data.get('minutes', 0)) * 60
                    interval += int(data.get('hours', 0)) * 3600
                    interval += int(data.get('days', 0)) * 86400

                    data['_seconds'] = interval

                    if not data['_next_fire_time']:
                        data['_next_fire_time'] = now + datetime.timedelta(seconds=data['_seconds'])

                    if interval < self.loop_interval:
                        self.loop_interval = interval

                data['_next_scheduled_fire_time'] = now + datetime.timedelta(seconds=data['_seconds'])

            elif 'once' in data:
                if data['_next_fire_time']:
                    if data['_next_fire_time'] < now - loop_interval or \
                       data['_next_fire_time'] > now and \
                       not data['_splay']:
                        continue

                if not data['_next_fire_time'] and not data['_splay']:
                    once = data['once']
                    if not isinstance(once, datetime.datetime):
                        once_fmt = data.get('once_fmt', '%Y-%m-%dT%H:%M:%S')
                        try:
                            once = datetime.datetime.strptime(data['once'],
                                                              once_fmt)
                        except (TypeError, ValueError):
                            log.error('Date string could not be parsed: %s, %s',
                                      data['once'], once_fmt)
                            continue
                    # If _next_fire_time is less than now or greater
                    # than now, continue.
                    if once < now - loop_interval:
                        continue
                    else:
                        data['_next_fire_time'] = once
                        data['_next_scheduled_fire_time'] = once

            elif 'when' in data:
                if not _WHEN_SUPPORTED:
                    log.error('Missing python-dateutil. Ignoring job %s.', job)
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
                                log.error(
                                    'Invalid date string %s. Ignoring job %s.',
                                    i, job
                                )
                                continue
                        _when.append(when__)

                    if data['_splay']:
                        _when.append(data['_splay'])

                    # Sort the list of "whens" from earlier to later schedules
                    _when.sort()

                    # Copy the list so we can loop through it
                    for i in copy.deepcopy(_when):
                        if len(_when) > 1:
                            if i < now - loop_interval:
                                # Remove all missed schedules except the latest one.
                                # We need it to detect if it was triggered previously.
                                _when.remove(i)

                    if _when:
                        # Grab the first element, which is the next run time or
                        # last scheduled time in the past.
                        when = _when[0]

                        if '_run' not in data:
                            # Prevent run of jobs from the past
                            data['_run'] = bool(when >= now - loop_interval)

                        if not data['_next_fire_time']:
                            data['_next_fire_time'] = when

                        data['_next_scheduled_fire_time'] = when

                        if data['_next_fire_time'] < when and \
                                not run and \
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
                            when = dateutil_parser.parse(_when)
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
                            when = dateutil_parser.parse(_when)
                        except ValueError:
                            log.error('Invalid date string. Ignoring')
                            continue
                    else:
                        when = data['when']
                        if not isinstance(when, datetime.datetime):
                            try:
                                when = dateutil_parser.parse(when)
                            except ValueError:
                                log.error('Invalid date string. Ignoring')
                                continue

                    if when < now - loop_interval and \
                            not data.get('_run', False) and \
                            not run and \
                            not data['_splay']:
                        data['_next_fire_time'] = None
                        continue

                    if '_run' not in data:
                        data['_run'] = True

                    if not data['_next_fire_time']:
                        data['_next_fire_time'] = when

                    data['_next_scheduled_fire_time'] = when

                    if data['_next_fire_time'] < when and \
                            not data['_run']:
                        data['_next_fire_time'] = when
                        data['_run'] = True

            elif 'cron' in data:
                if not _CRON_SUPPORTED:
                    log.error('Missing python-croniter. Ignoring job %s', job)
                    continue

                if data['_next_fire_time'] is None:
                    # Get next time frame for a "cron" job if it has been never
                    # executed before or already executed in the past.
                    try:
                        data['_next_fire_time'] = croniter.croniter(data['cron'], now).get_next(datetime.datetime)
                        data['_next_scheduled_fire_time'] = croniter.croniter(data['cron'], now).get_next(datetime.datetime)
                    except (ValueError, KeyError):
                        log.error('Invalid cron string. Ignoring')
                        continue

                    # If next job run is scheduled more than 1 minute ahead and
                    # configured loop interval is longer than that, we should
                    # shorten it to get our job executed closer to the beginning
                    # of desired time.
                    interval = (now - data['_next_fire_time']).total_seconds()
                    if interval >= 60 and interval < self.loop_interval:
                        self.loop_interval = interval

            else:
                continue

            seconds = (data['_next_fire_time'] - now).total_seconds()

            if 'splay' in data:
                # Got "splay" configured, make decision to run a job based on that
                if not data['_splay']:
                    # Try to add "splay" time only if next job fire time is
                    # still in the future. We should trigger job run
                    # immediately otherwise.
                    splay = _splay(data['splay'])
                    if now < data['_next_fire_time'] + datetime.timedelta(seconds=splay):
                        log.debug(
                            'schedule.handle_func: Adding splay of %s seconds '
                            'to next run.', splay
                        )
                        data['_splay'] = data['_next_fire_time'] + datetime.timedelta(seconds=splay)
                        if 'when' in data:
                            data['_run'] = True
                    else:
                        run = True

                if data['_splay']:
                    # The "splay" configuration has been already processed, just use it
                    seconds = (data['_splay'] - now).total_seconds()

            if '_seconds' in data:
                if seconds <= 0:
                    run = True
            elif 'when' in data and data['_run']:
                if data['_next_fire_time'] <= now <= (data['_next_fire_time'] + loop_interval):
                    data['_run'] = False
                    run = True
            elif 'cron' in data:
                # Reset next scheduled time because it is in the past now,
                # and we should trigger the job run, then wait for the next one.
                if seconds <= 0:
                    data['_next_fire_time'] = None
                    run = True
            elif 'once' in data:
                if data['_next_fire_time'] <= now <= (data['_next_fire_time'] + loop_interval):
                    run = True
            elif seconds == 0:
                run = True

            if '_run_on_start' in data and data['_run_on_start']:
                run = True
                data['_run_on_start'] = False
            elif run:
                if 'range' in data:
                    if not _RANGE_SUPPORTED:
                        log.error('Missing python-dateutil. Ignoring job %s', job)
                        continue
                    else:
                        if isinstance(data['range'], dict):
                            try:
                                start = dateutil_parser.parse(data['range']['start'])
                            except ValueError:
                                log.error('Invalid date string for start. Ignoring job %s.', job)
                                continue
                            try:
                                end = dateutil_parser.parse(data['range']['end'])
                            except ValueError:
                                log.error('Invalid date string for end. Ignoring job %s.', job)
                                continue
                            if end > start:
                                if 'invert' in data['range'] and data['range']['invert']:
                                    if now <= start or now >= end:
                                        run = True
                                    else:
                                        data['_skip_reason'] = 'in_skip_range'
                                        run = False
                                else:
                                    if start <= now <= end:
                                        run = True
                                    else:
                                        if self.skip_function:
                                            run = True
                                            func = self.skip_function
                                        else:
                                            data['_skip_reason'] = 'not_in_range'
                                            run = False
                            else:
                                log.error(
                                    'schedule.handle_func: Invalid range, end '
                                    'must be larger than start. Ignoring job %s.',
                                    job
                                )
                                continue
                        else:
                            log.error(
                                'schedule.handle_func: Invalid, range must be '
                                'specified as a dictionary. Ignoring job %s.',
                                job
                            )
                            continue

                # If there is no job specific skip_during_range available,
                # grab the global which defaults to None.
                if 'skip_during_range' not in data:
                    data['skip_during_range'] = self.skip_during_range

                if 'skip_during_range' in data and data['skip_during_range']:
                    if not _RANGE_SUPPORTED:
                        log.error('Missing python-dateutil. Ignoring job %s', job)
                        continue
                    else:
                        if isinstance(data['skip_during_range'], dict):
                            try:
                                start = dateutil_parser.parse(data['skip_during_range']['start'])
                            except ValueError:
                                log.error(
                                    'Invalid date string for start in '
                                    'skip_during_range. Ignoring job %s.',
                                    job
                                )
                                continue
                            try:
                                end = dateutil_parser.parse(data['skip_during_range']['end'])
                            except ValueError:
                                log.error(
                                    'Invalid date string for end in '
                                    'skip_during_range. Ignoring job %s.',
                                    job
                                )
                                log.error(data)
                                continue

                            # Check to see if we should run the job immediately
                            # after the skip_during_range is over
                            if 'run_after_skip_range' in data and \
                               data['run_after_skip_range']:
                                if 'run_explicit' not in data:
                                    data['run_explicit'] = []
                                # Add a run_explicit for immediately after the
                                # skip_during_range ends
                                _run_immediate = (end + loop_interval).strftime('%Y-%m-%dT%H:%M:%S')
                                if _run_immediate not in data['run_explicit']:
                                    data['run_explicit'].append({'time': _run_immediate,
                                                                 'time_fmt': '%Y-%m-%dT%H:%M:%S'})

                            if end > start:
                                if start <= now <= end:
                                    if self.skip_function:
                                        run = True
                                        func = self.skip_function
                                    else:
                                        run = False
                                    data['_skip_reason'] = 'in_skip_range'
                                    data['_skipped_time'] = now
                                    data['_skipped'] = True
                                else:
                                    run = True
                            else:
                                log.error(
                                    'schedule.handle_func: Invalid range, end '
                                    'must be larger than start. Ignoring job %s.',
                                    job
                                )
                                continue
                        else:
                            log.error(
                                'schedule.handle_func: Invalid, range must be '
                                'specified as a dictionary. Ignoring job %s.',
                                job
                            )
                            continue

                if 'skip_explicit' in data:
                    _skip_explicit = []
                    for _skip_time in data['skip_explicit']:
                        if isinstance(_skip_time, datetime.datetime):
                            _skip_explicit.append(_skip_time)
                        else:
                            _skip_explicit.append(datetime.datetime.strptime(_skip_time['time'],
                                                                             _skip_time['time_fmt']))

                    # Copy the list so we can loop through it
                    for i in copy.deepcopy(_skip_explicit):
                        if i < now - loop_interval:
                            _skip_explicit.remove(i)

                    if _skip_explicit:
                        if _skip_explicit[0] <= now <= (_skip_explicit[0] + loop_interval):
                            if self.skip_function:
                                run = True
                                func = self.skip_function
                            else:
                                run = False
                            data['_skip_reason'] = 'skip_explicit'
                            data['_skipped_time'] = now
                            data['_skipped'] = True
                        else:
                            run = True

                if 'until' in data:
                    if not _WHEN_SUPPORTED:
                        log.error('Missing python-dateutil. '
                                  'Ignoring until.')
                    else:
                        until = dateutil_parser.parse(data['until'])

                        if until <= now:
                            log.debug(
                                'Until time has passed skipping job: %s.',
                                data['name']
                            )
                            data['_skip_reason'] = 'until_passed'
                            data['_skipped_time'] = now
                            data['_skipped'] = True
                            run = False

                if 'after' in data:
                    if not _WHEN_SUPPORTED:
                        log.error('Missing python-dateutil. '
                                  'Ignoring after.')
                    else:
                        after = dateutil_parser.parse(data['after'])

                        if after >= now:
                            log.debug(
                                'After time has not passed skipping job: %s.',
                                data['name']
                            )
                            data['_skip_reason'] = 'after_not_passed'
                            data['_skipped_time'] = now
                            data['_skipped'] = True
                            run = False

            if not run:
                continue

            miss_msg = ''
            if seconds < 0:
                miss_msg = ' (runtime missed ' \
                           'by {0} seconds)'.format(abs(seconds))

            log.info('Running scheduled job: %s%s', job, miss_msg)

            if 'jid_include' not in data or data['jid_include']:
                data['jid_include'] = True
                log.debug('schedule: This job was scheduled with jid_include, '
                          'adding to cache (jid_include defaults to True)')
                if 'maxrunning' in data:
                    log.debug(
                        'schedule: This job was scheduled with a max number '
                        'of %s', data['maxrunning']
                    )
                else:
                    log.info(
                        'schedule: maxrunning parameter was not specified '
                        'for job %s, defaulting to 1.', job
                    )
                    data['maxrunning'] = 1

            multiprocessing_enabled = self.opts.get('multiprocessing', True)

            if salt.utils.platform.is_windows():
                # Temporarily stash our function references.
                # You can't pickle function references, and pickling is
                # required when spawning new processes on Windows.
                functions = self.functions
                self.functions = {}
                returners = self.returners
                self.returners = {}
            try:
                # Job is disabled, continue
                if 'enabled' in data and not data['enabled']:
                    log.debug('Job: %s is disabled', job)
                    data['_skip_reason'] = 'disabled'
                    continue
                else:
                    if not self.standalone:
                        data = self._check_max_running(func, data, self.opts)
                        run = data['run']

                    if run:
                        if multiprocessing_enabled:
                            thread_cls = salt.utils.process.SignalHandlingMultiprocessingProcess
                        else:
                            thread_cls = threading.Thread
                        proc = thread_cls(target=self.handle_func, args=(multiprocessing_enabled, func, data))

                        if multiprocessing_enabled:
                            with salt.utils.process.default_signals(signal.SIGINT, signal.SIGTERM):
                                # Reset current signals before starting the process in
                                # order not to inherit the current signal handlers
                                proc.start()
                        else:
                            proc.start()

                        if multiprocessing_enabled:
                            proc.join()
            finally:
                if '_seconds' in data:
                    data['_next_fire_time'] = now + datetime.timedelta(seconds=data['_seconds'])
                data['_last_run'] = now
                data['_splay'] = None
            if salt.utils.platform.is_windows():
                # Restore our function references.
                self.functions = functions
                self.returners = returners