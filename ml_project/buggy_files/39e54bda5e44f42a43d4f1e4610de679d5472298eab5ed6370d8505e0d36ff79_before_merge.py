    def __next__(self):
        # Try to get a batch, sometimes its possible that an iterator was
        # exhausted and thus we don't get a new batch
        success = False
        while not success:
            try:
                self._push_next()
                if self._rcvd_idx == self._sent_idx:
                    assert (
                        not self._data_buffer
                    ), "Data buffer should be empty at this moment"
                    raise StopIteration

                assert (
                    self._rcvd_idx < self._sent_idx
                ), "rcvd_idx must be smaller than sent_idx"
                assert (
                    self._rcvd_idx in self._data_buffer
                ), "fatal error with _push_next, rcvd_idx missing"
                ret = self._data_buffer.pop(self._rcvd_idx)

                got = ret.get(self._timeout)
                self._rcvd_idx += 1

                success, dataset_id, batch = pickle.loads(got)

                # If iterator exhausted/empty
                if not success:
                    self._exhausted_iterators.add(dataset_id)
                    if self.num_workers == len(self._exhausted_iterators):
                        # No more batches to be generated
                        return []
                    else:
                        self._push_next()
                else:
                    # either pin to cpu memory, or return with the right context straight away
                    batch = {
                        k: v.as_in_context(self.ctx)
                        if isinstance(
                            v, nd.NDArray
                        )  # context.cpu_pinned(self.pin_device_id)
                        else v
                        for k, v in batch.items()
                    }
                    return batch
            except multiprocessing.context.TimeoutError:
                print(
                    f"Worker timed out after {self._timeout} seconds. This might be caused by "
                    "\n - Slow transform. Please increase timeout to allow slower data loading in each worker. "
                    "\n - Insufficient shared_memory if `timeout` is large enough. "
                    "\n Please consider to reduce `num_workers` or increase shared_memory in system."
                )
                raise
            except Exception:
                self._worker_pool.terminate()
                raise