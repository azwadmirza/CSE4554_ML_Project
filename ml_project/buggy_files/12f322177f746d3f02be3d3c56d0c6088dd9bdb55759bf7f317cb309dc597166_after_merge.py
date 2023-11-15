    def tick(self, timeout):
        changed = False
        try:
            # This endless loop runs until the 'Queue.Empty'
            # exception is thrown.
            while True:
                mtype, obj = self.event_queue.get(timeout=timeout)
                handle_func = getattr(self, "handle_" + mtype)
                handle_func(obj)
                self.event_queue.task_done()
                changed = True
        except queue.Empty:
            pass
        return changed