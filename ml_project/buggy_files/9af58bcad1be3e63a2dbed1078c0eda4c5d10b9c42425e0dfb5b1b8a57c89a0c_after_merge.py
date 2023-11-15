    def run(self):
        '''
        Called when the process is started, and loops indefinitely
        until an error is encountered (typically an IOerror from the
        queue pipe being disconnected). During the loop, we attempt
        to pull tasks off the job queue and run them, pushing the result
        onto the results queue. We also remove the host from the blocked
        hosts list, to signify that they are ready for their next task.
        '''

        if HAS_ATFORK:
            atfork()

        try:
            # execute the task and build a TaskResult from the result
            debug("running TaskExecutor() for %s/%s" % (self._host, self._task))
            executor_result = TaskExecutor(
                self._host,
                self._task,
                self._task_vars,
                self._play_context,
                self._new_stdin,
                self._loader,
                self._shared_loader_obj,
            ).run()

            debug("done running TaskExecutor() for %s/%s" % (self._host, self._task))
            self._host.vars = dict()
            self._host.groups = []
            task_result = TaskResult(self._host, self._task, executor_result)

            # put the result on the result queue
            debug("sending task result")
            self._rslt_q.put(task_result)
            debug("done sending task result")

        except AnsibleConnectionFailure:
            self._host.vars = dict()
            self._host.groups = []
            task_result = TaskResult(self._host, self._task, dict(unreachable=True))
            self._rslt_q.put(task_result, block=False)

        except Exception as e:
            if not isinstance(e, (IOError, EOFError, KeyboardInterrupt)) or isinstance(e, TemplateNotFound):
                try:
                    self._host.vars = dict()
                    self._host.groups = []
                    task_result = TaskResult(self._host, self._task, dict(failed=True, exception=to_unicode(traceback.format_exc()), stdout=''))
                    self._rslt_q.put(task_result, block=False)
                except:
                    debug(u"WORKER EXCEPTION: %s" % to_unicode(e))
                    debug(u"WORKER EXCEPTION: %s" % to_unicode(traceback.format_exc()))

        debug("WORKER PROCESS EXITING")