    def _featurize_samples(self):
        try:
            if "train" in self.baskets[0].id:
                train_labels = []
                for basket in self.baskets:
                    for sample in basket.samples:
                        train_labels.append(sample.clear_text["label"])
                scaler = StandardScaler()
                scaler.fit(np.reshape(train_labels, (-1, 1)))
                self.label_list = [scaler.mean_.item(), scaler.scale_.item()]
                # Create label_maps because featurize is called after Processor instantiation
                self.label_maps = [{0:scaler.mean_.item(), 1:scaler.scale_.item()}]

        except Exception as e:
            logger.warning(f"Baskets not found: {e}")

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
            else:
                all_features_gen = map(
                    self._multiproc_featurize,
                    self.baskets
                )

            for basket_features, basket in tqdm(
                zip(all_features_gen, self.baskets), total=len(self.baskets)
            ):
                for f, s in zip(basket_features, basket.samples):
                    # Samples don't have labels during Inference mode
                    if "label" in s.clear_text:
                        label = s.clear_text["label"]
                        scaled_label = (label - self.label_list[0]) / self.label_list[1]
                        f[0]["label_ids"] = scaled_label
                    s.features = f