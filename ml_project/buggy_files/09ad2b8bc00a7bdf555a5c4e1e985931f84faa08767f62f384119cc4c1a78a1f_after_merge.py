    def add_task(self, wrapper, delay=0, task_name=None):
        assert wrapper

        reactor.callFromThread(lambda: self.register_task(self._check_task_name(task_name), self._reactor.callLater(delay, wrapper)))