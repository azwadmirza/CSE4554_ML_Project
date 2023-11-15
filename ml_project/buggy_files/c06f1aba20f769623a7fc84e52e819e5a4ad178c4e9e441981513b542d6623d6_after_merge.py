    def handle_func(self, multiprocessing_enabled, func, data):
        '''
        Execute this method in a multiprocess or thread
        '''
        if salt.utils.is_windows() or self.opts.get('transport') == 'zeromq':
            # Since function references can't be pickled and pickling
            # is required when spawning new processes on Windows, regenerate
            # the functions and returners.
            # This also needed for ZeroMQ transport to reset all functions
            # context data that could keep paretns connections. ZeroMQ will
            # hang on polling parents connections from the child process.
            if self.opts['__role'] == 'master':
                self.functions = salt.loader.runner(self.opts)
            else:
                self.functions = salt.loader.minion_mods(self.opts, proxy=self.proxy)
            self.returners = salt.loader.returners(self.opts, self.functions, proxy=self.proxy)
        ret = {'id': self.opts.get('id', 'master'),
               'fun': func,
               'fun_args': [],
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

        salt.utils.appendproctitle('{0} {1}'.format(self.__class__.__name__, ret['jid']))

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
            for job in salt.utils.minion.running(self.opts):
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

        if multiprocessing_enabled and not salt.utils.is_windows():
            # Reconfigure multiprocessing logging after daemonizing
            log_setup.setup_multiprocessing_logging()

        # Don't *BEFORE* to go into try to don't let it triple execute the finally section.
        salt.utils.daemonize_if(self.opts)

        # TODO: Make it readable! Splt to funcs, remove nested try-except-finally sections.
        try:
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
                ret['fun_args'].extend(data['args'])

            kwargs = {}
            if 'kwargs' in data:
                kwargs = data['kwargs']
                ret['fun_args'].append(data['kwargs'])

            if func not in self.functions:
                ret['return'] = self.functions.missing_fun_string(func)
                salt.utils.error.raise_error(
                    message=self.functions.missing_fun_string(func))

            # if the func support **kwargs, lets pack in the pub data we have
            # TODO: pack the *same* pub data as a minion?
            argspec = salt.utils.args.get_function_argspec(self.functions[func])
            if argspec.keywords:
                # this function accepts **kwargs, pack in the publish data
                for key, val in six.iteritems(ret):
                    kwargs['__pub_{0}'.format(key)] = val

            ret['return'] = self.functions[func](*args, **kwargs)

            data_returner = data.get('returner', None)
            if data_returner or self.schedule_returner:
                if 'return_config' in data:
                    ret['ret_config'] = data['return_config']
                if 'return_kwargs' in data:
                    ret['ret_kwargs'] = data['return_kwargs']
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

            # runners do not provide retcode
            if 'retcode' in self.functions.pack['__context__']:
                ret['retcode'] = self.functions.pack['__context__']['retcode']

            ret['success'] = True
        except Exception:
            log.exception("Unhandled exception running {0}".format(ret['fun']))
            # Although catch-all exception handlers are bad, the exception here
            # is to let the exception bubble up to the top of the thread context,
            # where the thread will die silently, which is worse.
            if 'return' not in ret:
                ret['return'] = "Unhandled exception running {0}".format(ret['fun'])
            ret['success'] = False
            ret['retcode'] = 254
        finally:
            try:
                # Only attempt to return data to the master
                # if the scheduled job is running on a minion.
                if '__role' in self.opts and self.opts['__role'] == 'minion':
                    if 'return_job' in data and not data['return_job']:
                        pass
                    else:
                        # Send back to master so the job is included in the job list
                        mret = ret.copy()
                        mret['jid'] = 'req'
                        if data.get('return_job') == 'nocache':
                            # overwrite 'req' to signal to master that this job shouldn't be stored
                            mret['jid'] = 'nocache'
                        event = salt.utils.event.get_event('minion', opts=self.opts, listen=False)
                        load = {'cmd': '_return', 'id': self.opts['id']}
                        for key, value in six.iteritems(mret):
                            load[key] = value
                        event.fire_event(load, '__schedule_return')

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
            finally:
                if multiprocessing_enabled:
                    # Let's make sure we exit the process!
                    sys.exit(salt.defaults.exitcodes.EX_GENERIC)