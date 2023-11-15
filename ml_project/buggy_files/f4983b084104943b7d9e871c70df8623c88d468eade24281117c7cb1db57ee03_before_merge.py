    def handle_func(self, func, data):
        '''
        Execute this method in a multiprocess or thread
        '''
        if salt.utils.is_windows():
            self.functions = salt.loader.minion_mods(self.opts)
            self.returners = salt.loader.returners(self.opts, self.functions)
        ret = {'id': self.opts.get('id', 'master'),
               'fun': func,
               'schedule': data['name'],
               'jid': '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())}

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
                fn = os.path.join(salt.minion.get_proc_dir(self.opts['cachedir']), basefilename)
                with salt.utils.fopen(fn, 'r') as fp_:
                    job = salt.payload.Serial(self.opts).load(fp_)
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

        salt.utils.daemonize_if(self.opts)

        ret['pid'] = os.getpid()

        if 'jid_include' not in data or data['jid_include']:
            log.debug('schedule.handle_func: adding this job to the jobcache '
                      'with data {0}'.format(ret))
            # write this to /var/cache/salt/minion/proc
            with salt.utils.fopen(proc_fn, 'w+') as fp_:
                fp_.write(salt.payload.Serial(self.opts).dumps(ret))

        args = None
        if 'args' in data:
            args = data['args']

        kwargs = None
        if 'kwargs' in data:
            kwargs = data['kwargs']

        try:
            if args and kwargs:
                ret['return'] = self.functions[func](*args, **kwargs)

            if args and not kwargs:
                ret['return'] = self.functions[func](*args)

            if kwargs and not args:
                ret['return'] = self.functions[func](**kwargs)

            if not kwargs and not args:
                ret['return'] = self.functions[func]()

            data_returner = data.get('returner', None)
            if data_returner or self.schedule_returner:
                rets = []
                for returner in [data_returner, self.schedule_returner]:
                    if isinstance(returner, str):
                        rets.append(returner)
                    elif isinstance(returner, list):
                        rets.extend(returner)
                # simple de-duplication with order retained
                rets = OrderedDict.fromkeys(rets).keys()
                for returner in rets:
                    ret_str = '{0}.returner'.format(returner)
                    if ret_str in self.returners:
                        ret['success'] = True
                        self.returners[ret_str](ret)
                    else:
                        log.info(
                            'Job {0} using invalid returner: {1} Ignoring.'.format(
                            func, returner
                            )
                        )
        except Exception:
            log.exception("Unhandled exception running {0}".format(ret['fun']))
            # Although catch-all exception handlers are bad, the exception here
            # is to let the exception bubble up to the top of the thread context,
            # where the thread will die silently, which is worse.
        finally:
            try:
                os.unlink(proc_fn)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    # EEXIST is OK because the file is gone and that's what
                    # we wanted
                    pass
                else:
                    log.error("Failed to delete '{0}': {1}".format(proc_fn, e.errno))
                    # Otherwise, failing to delete this file is not something
                    # we can cleanly handle.
                    raise