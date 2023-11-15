    def _submit_operand_to_execute(self):
        self._semaphore.acquire()
        self._queue.wait()

        if self._has_error.is_set():
            # error happens, ignore
            return

        to_submit_op = self._queue.pop(0)
        assert to_submit_op.key not in self._submitted_op_keys
        self._submitted_op_keys.add(to_submit_op.key)

        if self._print_progress:
            i, n = len(self._submitted_op_keys), len(self._op_key_to_ops)
            if i % 30 or i >= n:
                logger.info('[{0}] {1:.2f}% percent of graph has been submitted'.format(
                    str(datetime.datetime.now()), float(i) * 100 / n))

        if self._prefetch:
            # check the operand's outputs if any of its successor's predecessors can be prefetched
            self._prefetch_executor.submit(self._fetch_chunks, to_submit_op.outputs)
        # execute the operand and return future
        return self._operand_executor.submit(self._execute_operand, to_submit_op)