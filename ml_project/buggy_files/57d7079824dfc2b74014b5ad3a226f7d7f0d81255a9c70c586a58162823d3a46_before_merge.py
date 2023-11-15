    def call(self):
        '''
        Call the module
        '''
        ret = {}
        fun = self.opts['fun']
        ret['jid'] = '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now())
        proc_fn = os.path.join(
            salt.minion.get_proc_dir(self.opts['cachedir']),
            ret['jid']
        )
        if fun not in self.minion.functions:
            sys.stderr.write('Function {0} is not available\n'.format(fun))
            sys.exit(-1)
        try:
            args, kwargs = salt.minion.parse_args_and_kwargs(
                self.minion.functions[fun], self.opts['arg'])
            sdata = {
                    'fun': fun,
                    'pid': os.getpid(),
                    'jid': ret['jid'],
                    'tgt': 'salt-call'}
            try:
                with salt.utils.fopen(proc_fn, 'w+') as fp_:
                    fp_.write(self.serial.dumps(sdata))
            except NameError:
                # Don't require msgpack with local
                pass
            func = self.minion.functions[fun]
            ret['return'] = func(*args, **kwargs)
            ret['retcode'] = sys.modules[func.__module__].__context__.get(
                    'retcode', 0)
        except (CommandExecutionError) as exc:
            msg = 'Error running \'{0}\': {1}\n'
            active_level = LOG_LEVELS.get(
                self.opts['log_level'].lower(), logging.ERROR)
            if active_level <= logging.DEBUG:
                sys.stderr.write(traceback.format_exc())
            sys.stderr.write(msg.format(fun, str(exc)))
            sys.exit(1)
        except CommandNotFoundError as exc:
            msg = 'Command required for \'{0}\' not found: {1}\n'
            sys.stderr.write(msg.format(fun, str(exc)))
            sys.exit(1)
        try:
            os.remove(proc_fn)
        except (IOError, OSError):
            pass
        if hasattr(self.minion.functions[fun], '__outputter__'):
            oput = self.minion.functions[fun].__outputter__
            if isinstance(oput, string_types):
                ret['out'] = oput
        if self.opts.get('return', ''):
            ret['id'] = self.opts['id']
            ret['fun'] = fun
            for returner in self.opts['return'].split(','):
                try:
                    self.minion.returners['{0}.returner'.format(returner)](ret)
                except Exception:
                    pass
        return ret