        def delayed_call(delay, task_name):
            self.register_task(self._check_task_name(task_name), self._reactor.callLater(delay, reactor.callInThread, wrapper))