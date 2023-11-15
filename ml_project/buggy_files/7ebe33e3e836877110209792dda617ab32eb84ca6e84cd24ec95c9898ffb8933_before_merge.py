    def _execute_operand(self, op):
        results = self._chunk_results
        ref_counts = self._chunk_key_ref_counts
        op_keys = self._executed_op_keys
        try:
            ops = list(self._op_key_to_ops[op.key])
            if not self._mock:
                # do real execution
                # note that currently execution is the chunk-level
                # so we pass the first operand's first output to Executor.handle
                first_op = ops[0]
                Executor.handle(first_op.outputs[0], results)
                op_keys.add(first_op.key)
                # handle other operands
                for rest_op in ops[1:]:
                    for op_output, rest_op_output in zip(first_op.outputs, rest_op.outputs):
                        results[rest_op_output.key] = results[op_output.key]
            else:
                sparse_percent = self._sparse_mock_percent if op.sparse else 1.0
                for output in op.outputs:
                    results[output.key] = output.nbytes * sparse_percent

            with self._lock:
                for output in itertools.chain(*[op.outputs for op in ops]):
                    # in case that operand has multiple outputs
                    # and some of the output not in result keys, delete them
                    if ref_counts.get(output.key) == 0:
                        del results[output.key]

                    # clean the predecessors' results if ref counts equals 0
                    for pred_chunk in self._graph.iter_predecessors(output):
                        if pred_chunk.key in ref_counts:
                            ref_counts[pred_chunk.key] -= 1
                            if ref_counts[pred_chunk.key] == 0:
                                del results[pred_chunk.key]

                    # add successors' operands to queue
                    for succ_chunk in self._graph.iter_successors(output):
                        preds = self._graph.predecessors(succ_chunk)
                        if succ_chunk.op.key not in self._submitted_op_keys and \
                                (len(preds) == 0 or all(pred.op.key in op_keys for pred in preds)):
                            self._queue.insert(0, succ_chunk.op)
        except Exception:
            self._has_error.set()
            raise
        finally:
            self._semaphore.release()