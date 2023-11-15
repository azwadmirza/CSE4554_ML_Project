    def loop(self):
        self._init_readers()

        while self._num_running > 0:
            try:
                item, exception = self.queue.get(timeout=0.1)

                if exception:
                    raise exception

                if item is STOP:
                    self._num_running -= 1
                else:
                    yield item
            except Empty:
                pass