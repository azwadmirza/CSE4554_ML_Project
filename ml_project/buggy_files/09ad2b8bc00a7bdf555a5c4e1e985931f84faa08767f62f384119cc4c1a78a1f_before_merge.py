    def add_task(self, wrapper, delay=0, task_name=None):
        assert wrapper

        if not task_name:
            with self._lock:
                self._auto_counter += 1
            task_name = "threadpool_manager %d" % self._auto_counter
        reactor.callFromThread(lambda: self.register_task(task_name, self._reactor.callLater(delay, wrapper)))