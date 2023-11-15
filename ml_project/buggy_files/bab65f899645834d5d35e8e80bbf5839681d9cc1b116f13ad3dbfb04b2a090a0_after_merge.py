    def proc_run(self, msg):
        '''
        Execute the run in a dedicated process
        '''
        data = msg['pub']
        fn_ = os.path.join(self.proc_dir, data['jid'])
        self.opts['__ex_id'] = data['jid']
        salt.utils.daemonize_if(self.opts)

        salt.transport.jobber_stack = stack = self._setup_jobber_stack()
        # set up return destination from source
        src_estate, src_yard, src_share = msg['route']['src']
        salt.transport.jobber_estate_name = src_estate
        salt.transport.jobber_yard_name = src_yard

        sdata = {'pid': os.getpid()}
        sdata.update(data)
        with salt.utils.fopen(fn_, 'w+b') as fp_:
            fp_.write(self.serial.dumps(sdata))
        ret = {'success': False}
        function_name = data['fun']
        if function_name in self.modules.value:
            try:
                func = self.modules.value[data['fun']]
                args, kwargs = salt.minion.load_args_and_kwargs(
                    func,
                    salt.utils.args.parse_input(
                        data['arg'],
                        no_parse=data.get('no_parse', [])),
                    data)
                sys.modules[func.__module__].__context__['retcode'] = 0

                executors = data.get('module_executors') or self.opts.get('module_executors', ['direct_call.get'])
                if isinstance(executors, six.string_types):
                    executors = [executors]
                elif not isinstance(executors, list) or not executors:
                    raise SaltInvocationError("Wrong executors specification: {0}. String or non-empty list expected".
                                              format(executors))
                if self.opts.get('sudo_user', '') and executors[-1] != 'sudo.get':
                    if executors[-1] in FUNCTION_EXECUTORS:
                        executors[-1] = 'sudo.get'  # replace
                    else:
                        executors.append('sudo.get')  # append
                log.trace("Executors list {0}".format(executors))

                # Get executors
                def get_executor(name):
                    executor_class = self.module_executors.value.get(name)
                    if executor_class is None:
                        raise SaltInvocationError("Executor '{0}' is not available".format(name))
                    return executor_class
                # Get the last one that is function executor
                executor = get_executor(executors.pop())(self.opts, data, func, args, kwargs)
                # Instantiate others from bottom to the top
                for executor_name in reversed(executors):
                    executor = get_executor(executor_name)(self.opts, data, executor)
                return_data = executor.execute()

                if isinstance(return_data, types.GeneratorType):
                    ind = 0
                    iret = {}
                    for single in return_data:
                        if isinstance(single, dict) and isinstance(iret, list):
                            iret.update(single)
                        else:
                            if not iret:
                                iret = []
                            iret.append(single)
                        tag = tagify(
                                [data['jid'], 'prog', self.opts['id'], str(ind)],
                                'job')
                        event_data = {'return': single}
                        self._fire_master(event_data, tag)  # Need to look into this
                        ind += 1
                    ret['return'] = iret
                else:
                    ret['return'] = return_data
                ret['retcode'] = sys.modules[func.__module__].__context__.get(
                    'retcode',
                    0
                )
                ret['success'] = True
            except CommandNotFoundError as exc:
                msg = 'Command required for \'{0}\' not found'.format(
                    function_name
                )
                log.debug(msg, exc_info=True)
                ret['return'] = '{0}: {1}'.format(msg, exc)
            except CommandExecutionError as exc:
                log.error(
                    'A command in \'{0}\' had a problem: {1}'.format(
                        function_name,
                        exc
                    ),
                    exc_info_on_loglevel=logging.DEBUG
                )
                ret['return'] = 'ERROR: {0}'.format(exc)
            except SaltInvocationError as exc:
                log.error(
                    'Problem executing \'{0}\': {1}'.format(
                        function_name,
                        exc
                    ),
                    exc_info_on_loglevel=logging.DEBUG
                )
                ret['return'] = 'ERROR executing \'{0}\': {1}'.format(
                    function_name, exc
                )
            except TypeError as exc:
                msg = ('TypeError encountered executing {0}: {1}. See '
                       'debug log for more info.').format(function_name, exc)
                log.warning(msg, exc_info_on_loglevel=logging.DEBUG)
                ret['return'] = msg
            except Exception:
                msg = 'The minion function caused an exception'
                log.warning(msg, exc_info_on_loglevel=logging.DEBUG)
                ret['return'] = '{0}: {1}'.format(msg, traceback.format_exc())
        else:
            ret['return'] = '\'{0}\' is not available.'.format(function_name)

        ret['jid'] = data['jid']
        ret['fun'] = data['fun']
        ret['fun_args'] = data['arg']
        self._return_pub(msg, ret, stack)
        if data['ret']:
            ret['id'] = self.opts['id']
            for returner in set(data['ret'].split(',')):
                try:
                    self.returners.value['{0}.returner'.format(
                        returner
                    )](ret)
                except Exception as exc:
                    log.error(
                        'The return failed for job {0} {1}'.format(
                        data['jid'],
                        exc
                        )
                    )
        console.concise("Closing Jobber Stack {0}\n".format(stack.name))
        stack.server.close()
        salt.transport.jobber_stack = None