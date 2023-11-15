    def _read_worker_result(self):
        result = None
        starting_point = self._cur_worker
        while True:
            (worker_prc, main_q, rslt_q) = self._workers[self._cur_worker]
            self._cur_worker += 1
            if self._cur_worker >= len(self._workers):
                self._cur_worker = 0

            try:
                if rslt_q.qsize() > 0:
                    debug("worker %d has data to read" % self._cur_worker)
                    result = rslt_q.get()
                    debug("got a result from worker %d: %s" % (self._cur_worker, result))
                    break
            except queue.Empty:
                pass

            if self._cur_worker == starting_point:
                break

        return result