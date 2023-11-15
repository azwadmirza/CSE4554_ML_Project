    def _init_samples_in_baskets(self):
        with ExitStack() as stack:
            if self.use_multiprocessing:
                chunks_to_process = int(len(self.baskets) / self.multiprocessing_chunk_size)
                num_cpus = min(mp.cpu_count(), self.max_processes, chunks_to_process) or 1

                logger.info(
                    f"Got ya {num_cpus} parallel workers to fill the baskets with samples (chunksize = {self.multiprocessing_chunk_size})..."
                )
                p = stack.enter_context(mp.Pool(processes=num_cpus))
                manager = stack.enter_context(mp.Manager())

                if self.share_all_baskets_for_multiprocessing:
                    all_dicts = manager.list([b.raw for b in self.baskets])
                else:
                    all_dicts = None

                samples = p.imap(
                    partial(self._multiproc_sample, all_dicts=all_dicts),
                    self.baskets,
                    chunksize=self.multiprocessing_chunk_size,
                )
            else:
                all_dicts = [b.raw for b in self.baskets]
                samples = map(
                    partial(self._multiproc_sample, all_dicts=all_dicts),
                    self.baskets
                )

            for s, b in tqdm(
                    zip(samples, self.baskets), total=len(self.baskets)
            ):
                b.samples = s