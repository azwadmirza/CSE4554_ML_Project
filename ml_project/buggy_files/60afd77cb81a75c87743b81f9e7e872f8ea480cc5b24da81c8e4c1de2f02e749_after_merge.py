    def add_task_in_thread(self, wrapper, delay=0, task_name=None):
        assert wrapper

        def delayed_call(delay, task_name):
            self.register_task(self._check_task_name(task_name), self._reactor.callLater(delay, reactor.callInThread, wrapper))

        reactor.callFromThread(delayed_call, delay, task_name)