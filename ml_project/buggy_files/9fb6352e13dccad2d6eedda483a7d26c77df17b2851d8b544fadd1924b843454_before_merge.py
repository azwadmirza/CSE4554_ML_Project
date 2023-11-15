    def __iter__(self):
        self.cycle_num += 1
        if self.num_workers == 0:
            generator = sequential_sample_generator(
                self.dataset, self.transformation, self.is_train, self.cyclic
            )

            def same_process_iter():
                while True:
                    # take the next batch size elements
                    sample_batch = list(
                        itertools.islice(generator, self.batch_size)
                    )

                    # terminate if no more batches to be dealt with
                    if len(sample_batch) == 0:
                        return

                    # make them into a single batch
                    batch = self.batchify_fn(
                        data=sample_batch,
                        parallel_processing=False,
                        dtype=self.dtype,
                    )

                    # either pin to cpu memory, or return with the right context straight away
                    batch = {
                        k: v.as_in_context(self.ctx)
                        if isinstance(
                            v, nd.NDArray
                        )  # context.cpu_pinned(self.pin_device_id)
                        else v
                        for k, v in batch.items()
                    }
                    yield batch

            return same_process_iter()
        else:
            # multi-worker takes care of asynchronously preparing batches
            # only cache multi_worker for cyclic datasets
            if self.multi_worker_cache is None:
                multi_worker = _MultiWorkerIter(
                    worker_pool=self.worker_pool,
                    num_workers=self.num_workers,
                    batch_size=self.batch_size,
                    shuffle=self.shuffle,
                    batchify_fn=self.batchify_fn,
                    dtype=self.dtype,
                    ctx=self.ctx,
                    is_train=self.is_train,
                    cyclic=self.cyclic,
                    worker_fn=_worker_fn,
                    num_prefetch=self.num_prefetch,
                    dataset_len=self.dataset_len,
                    cycle_num=self.cycle_num,
                )
                if self.cyclic:
                    self.multi_worker_cache = iter(multi_worker)
                return iter(multi_worker)
            else:
                # This way we can recycle the unused pre-fetched batches for the next epoch
                # (cycle num is irrelevant for cyclic datasets, and rest of the arguments stays same between epochs)
                return self.multi_worker_cache