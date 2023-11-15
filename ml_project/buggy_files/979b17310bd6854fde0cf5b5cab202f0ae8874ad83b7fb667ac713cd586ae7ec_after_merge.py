    def _featurize_samples(self):
        with ExitStack() as stack:
            if self.use_multiprocessing:
                chunks_to_process = int(len(self.baskets) / self.multiprocessing_chunk_size)
                num_cpus = min(mp.cpu_count(), self.max_processes, chunks_to_process) or 1
                logger.info(
                    f"Got ya {num_cpus} parallel workers to featurize samples in baskets (chunksize = {self.multiprocessing_chunk_size}) ..."
                )

                p = stack.enter_context(mp.Pool(processes=num_cpus))
                all_features_gen = p.imap(
                    self._multiproc_featurize,
                    self.baskets,
                    chunksize=self.multiprocessing_chunk_size,
                )

                for basket_features, basket in tqdm(
                        zip(all_features_gen, self.baskets), total=len(self.baskets)
                ):
                    for f, s in zip(basket_features, basket.samples):
                        s.features = f
            else:
                all_features_gen = map(
                    self._multiproc_featurize,
                    self.baskets
                )

            for basket_features, basket in tqdm(
                zip(all_features_gen, self.baskets), total=len(self.baskets)
            ):
                for f, s in zip(basket_features, basket.samples):
                    s.features = f