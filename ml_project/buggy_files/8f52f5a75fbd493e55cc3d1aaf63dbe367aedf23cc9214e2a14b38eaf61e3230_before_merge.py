        def delayed_call(delay, task_name):
            self.register_task(task_name, self._reactor.callLater(delay, reactor.callInThread, wrapper))