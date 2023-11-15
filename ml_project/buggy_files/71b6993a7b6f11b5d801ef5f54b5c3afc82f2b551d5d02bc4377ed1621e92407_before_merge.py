    def handle_func(self, func, data):
        '''
        Execute this method in a multiprocess or thread
        '''
        if salt.utils.is_windows():
            # Since function references can't be pickled and pickling
            # is required when spawning new processes on Windows, regenerate
            # the functions and returners.
            self.functions = salt.loader.minion_mods(self.opts)
            self.returners = salt.loader.returners(self.opts, self.functions)
        ret = {'id': self.opts.get('id', 'master'),
               'fun': func,
               'schedule': data['name'],
               'jid': salt.utils.jid.gen_jid()}

        if 'metadata' in data:
            if isinstance(data['metadata'], dict):
                ret['metadata'] = data['metadata']
                ret['metadata']['_TOS'] = self.time_offset
                ret['metadata']['_TS'] = time.ctime()
                ret['metadata']['_TT'] = time.strftime('%Y %B %d %a %H %m', time.gmtime())
            else:
                log.warning('schedule: The metadata parameter must be '
                            'specified as a dictionary.  Ignoring.')

        salt.utils.appendproctitle(ret['jid'])

        proc_fn = os.path.join(
            salt.minion.get_proc_dir(self.opts['cachedir']),
            ret['jid']
        )

        # Check to see if there are other jobs with this
        # signature running.  If there are more than maxrunning
        # jobs present then don't start another.
        # If jid_include is False for this job we can ignore all this
        # NOTE--jid_include defaults to True, thus if it is missing from the data
        # dict we treat it like it was there and is True
        if 'jid_include' not in data or data['jid_include']:
            jobcount = 0
            for basefilename in os.listdir(salt.minion.get_proc_dir(self.opts['cachedir'])):
                fn_ = os.path.join(salt.minion.get_proc_dir(self.opts['cachedir']), basefilename)
                if not os.path.exists(fn_):
                    log.debug('schedule.handle_func: {0} was processed '
                              'in another thread, skipping.'.format(
                                  basefilename))
                    continue
                with salt.utils.fopen(fn_, 'rb') as fp_:
                    job = salt.payload.Serial(self.opts).load(fp_)
                    if job:
                        if 'schedule' in job:
                            log.debug('schedule.handle_func: Checking job against '
                                      'fun {0}: {1}'.format(ret['fun'], job))
                            if ret['schedule'] == job['schedule'] and os_is_running(job['pid']):
                                jobcount += 1
                                log.debug(
                                    'schedule.handle_func: Incrementing jobcount, now '
                                    '{0}, maxrunning is {1}'.format(
                                        jobcount, data['maxrunning']))
                                if jobcount >= data['maxrunning']:
                                    log.debug(
                                        'schedule.handle_func: The scheduled job {0} '
                                        'was not started, {1} already running'.format(
                                            ret['schedule'], data['maxrunning']))
                                    return False
                    else:
                        try:
                            log.info('Invalid job file found.  Removing.')
                            os.remove(fn_)
                        except OSError:
                            log.info('Unable to remove file: {0}.'.format(fn_))

        salt.utils.daemonize_if(self.opts)

        ret['pid'] = os.getpid()

        if 'jid_include' not in data or data['jid_include']:
            log.debug('schedule.handle_func: adding this job to the jobcache '
                      'with data {0}'.format(ret))
            # write this to /var/cache/salt/minion/proc
            with salt.utils.fopen(proc_fn, 'w+b') as fp_:
                fp_.write(salt.payload.Serial(self.opts).dumps(ret))

        args = tuple()
        if 'args' in data:
            args = data['args']

        kwargs = {}
        if 'kwargs' in data:
            kwargs = data['kwargs']
        # if the func support **kwargs, lets pack in the pub data we have
        # TODO: pack the *same* pub data as a minion?
        argspec = salt.utils.args.get_function_argspec(self.functions[func])
        if argspec.keywords:
            # this function accepts **kwargs, pack in the publish data
            for key, val in six.iteritems(ret):
                kwargs['__pub_{0}'.format(key)] = val

        try:
            ret['return'] = self.functions[func](*args, **kwargs)

            data_returner = data.get('returner', None)
            if data_returner or self.schedule_returner:
                if 'returner_config' in data:
                    ret['ret_config'] = data['returner_config']
                rets = []
                for returner in [data_returner, self.schedule_returner]:
                    if isinstance(returner, str):
                        rets.append(returner)
                    elif isinstance(returner, list):
                        rets.extend(returner)
                # simple de-duplication with order retained
                for returner in OrderedDict.fromkeys(rets):
                    ret_str = '{0}.returner'.format(returner)
                    if ret_str in self.returners:
                        ret['success'] = True
                        self.returners[ret_str](ret)
                    else:
                        log.info(
                            'Job {0} using invalid returner: {1}. Ignoring.'.format(
                                func, returner
                            )
                        )

            if 'return_job' in data and not data['return_job']:
                pass
            else:
                # Send back to master so the job is included in the job list
                mret = ret.copy()
                mret['jid'] = 'req'
                channel = salt.transport.Channel.factory(self.opts, usage='salt_schedule')
                load = {'cmd': '_return', 'id': self.opts['id']}
                for key, value in six.iteritems(mret):
                    load[key] = value
                channel.send(load)

        except Exception:
            log.exception("Unhandled exception running {0}".format(ret['fun']))
            # Although catch-all exception handlers are bad, the exception here
            # is to let the exception bubble up to the top of the thread context,
            # where the thread will die silently, which is worse.
        finally:
            try:
                log.debug('schedule.handle_func: Removing {0}'.format(proc_fn))
                os.unlink(proc_fn)
            except OSError as exc:
                if exc.errno == errno.EEXIST or exc.errno == errno.ENOENT:
                    # EEXIST and ENOENT are OK because the file is gone and that's what
                    # we wanted
                    pass
                else:
                    log.error("Failed to delete '{0}': {1}".format(proc_fn, exc.errno))
                    # Otherwise, failing to delete this file is not something
                    # we can cleanly handle.
                    raise