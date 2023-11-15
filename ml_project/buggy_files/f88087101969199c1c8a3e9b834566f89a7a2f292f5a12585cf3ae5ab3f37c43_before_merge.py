    def _init_samples_in_baskets(self):
        chunks_to_process = int(len(self.baskets) / self.multiprocessing_chunk_size)
        num_cpus = min(mp.cpu_count(), self.max_processes, chunks_to_process) or 1

        logger.info(
            f"Got ya {num_cpus} parallel workers to fill the baskets with samples (chunksize = {self.multiprocessing_chunk_size})..."
        )

        with mp.Pool(processes=num_cpus) as p:
            with mp.Manager() as manager:
                if self.share_all_baskets_for_multiprocessing:
                    all_dicts = manager.list([b.raw for b in self.baskets])
                else:
                    all_dicts = None

                with mp.Pool(processes=num_cpus) as p:
                    samples = p.imap(
                        partial(self._multiproc_sample, all_dicts=all_dicts),
                        self.baskets,
                        chunksize=self.multiprocessing_chunk_size,
                    )

                    for s, b in tqdm(
                        zip(samples, self.baskets), total=len(self.baskets)
                    ):
                        b.samples = s