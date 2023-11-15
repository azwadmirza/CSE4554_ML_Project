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