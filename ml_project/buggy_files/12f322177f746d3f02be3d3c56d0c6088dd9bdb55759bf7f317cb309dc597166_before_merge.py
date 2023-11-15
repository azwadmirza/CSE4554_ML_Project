    def tick(self, q, timeout):
        changed = False
        try:
            # This endless loop runs until the 'Queue.Empty'
            # exception is thrown. If more than one request is in
            # the queue, this speeds up every request by 0.1 seconds,
            # because get_input(..) function is not blocking.
            while True:
                msg = q.get(timeout=timeout)
                self.handle(*msg)
                q.task_done()
                changed = True
        except queue.Empty:
            pass
        return changed