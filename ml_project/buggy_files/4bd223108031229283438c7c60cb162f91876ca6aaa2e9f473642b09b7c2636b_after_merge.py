    def submit(self, func, *args, parsl_sites='all', fn_hash=None, cache=False, **kwargs):
        """Add task to the dataflow system.

        >>> IF all deps are met :
        >>>   send to the runnable queue and launch the task
        >>> ELSE:
        >>>   post the task in the pending queue

        Args:
            - func : A function object
            - *args : Args to the function

        KWargs :
            - parsl_sites (List|String) : List of sites this call could go to.
                    Default='all'
            - fn_hash (Str) : Hash of the function and inputs
                    Default=None
            - cache (Bool) : To enable memoization or not
            - kwargs (dict) : Rest of the kwargs to the fn passed as dict.

        Returns:
               (AppFuture) [DataFutures,]

        """
        task_id = self.task_count
        self.task_count += 1

        # Get the dep count and a list of dependencies for the task
        dep_cnt, depends = self._count_all_deps(task_id, args, kwargs)

        task_def = {'depends': depends,
                    'sites': parsl_sites,
                    'func': func,
                    'func_name': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                    'fn_hash': fn_hash,
                    'memoize': cache,
                    'callback': None,
                    'dep_cnt': dep_cnt,
                    'exec_fu': None,
                    'checkpoint': None,
                    'fail_count': 0,
                    'fail_history': [],
                    'env': None,
                    'status': States.unsched,
                    'app_fu': None}

        if task_id in self.tasks:
            raise DuplicateTaskError(
                "Task {0} in pending list".format(task_id))
        else:
            self.tasks[task_id] = task_def

        # Extract stdout and stderr to pass to AppFuture:
        task_stdout = kwargs.get('stdout', None)
        task_stderr = kwargs.get('stderr', None)

        logger.info("Task {} submitted for App {}, waiting on tasks {}".format(task_id,
                                                                               task_def['func_name'],
                                                                               [fu.tid for fu in depends]))

        # Handle three cases here:
        # No pending deps
        #     - But has failures -> dep_fail
        #     - No failures -> running
        # Has pending deps -> pending
        if dep_cnt == 0:

            new_args, kwargs, exceptions = self.sanitize_and_wrap(
                task_id, args, kwargs)
            self.tasks[task_id]['args'] = new_args
            self.tasks[task_id]['kwargs'] = kwargs

            if not exceptions:
                self.tasks[task_id]['exec_fu'] = self.launch_task(
                    task_id, func, *new_args, **kwargs)
                self.tasks[task_id]['app_fu'] = AppFuture(self.tasks[task_id]['exec_fu'],
                                                          tid=task_id,
                                                          stdout=task_stdout,
                                                          stderr=task_stderr)
                logger.debug("Task {} launched with AppFut:{}".format(task_id,
                                                                      task_def['app_fu']))

            else:
                self.tasks[task_id]['exec_fu'] = None
                app_fu = AppFuture(self.tasks[task_id]['exec_fu'],
                                   tid=task_id,
                                   stdout=task_stdout,
                                   stderr=task_stderr)
                app_fu.set_exception(DependencyError(exceptions,
                                                     "Failures in input dependencies",
                                                     None))
                self.tasks[task_id]['app_fu'] = app_fu
                self.tasks[task_id]['status'] = States.dep_fail
                logger.debug("Task {} failed due to failure in parent task(s):{}".format(task_id,
                                                                                         task_def['app_fu']))

        else:
            # Send to pending, create the AppFuture with no parent and have it set
            # when an executor future is available.
            self.tasks[task_id]['app_fu'] = AppFuture(None, tid=task_id,
                                                      stdout=task_stdout,
                                                      stderr=task_stderr)
            self.tasks[task_id]['status'] = States.pending
            logger.debug("Task {} launched with AppFut:{}".format(task_id,
                                                                  task_def['app_fu']))

        return task_def['app_fu']