    def _get_dataset(self, filename):
        dicts = self.processor.file_to_dicts(filename)
        #shuffle list of dicts here if we later want to have a random dev set splitted from train set
        if self.processor.train_filename in filename:
            if not self.processor.dev_filename:
                if self.processor.dev_split > 0.0:
                    random.shuffle(dicts)

        num_cpus = min(mp.cpu_count(), self.max_processes) or 1
        dicts_per_cpu = np.ceil(len(dicts) / num_cpus)
        # automatic adjustment of multiprocessing chunksize
        # for small files (containing few dicts) we want small chunksize to ulitize all available cores but never less
        # than 2, because we need it to sample another random sentence in LM finetuning
        # for large files we want to minimize processor spawning without giving too much data to one process, so we
        # clip it at 5k
        multiprocessing_chunk_size = int(np.clip((np.ceil(dicts_per_cpu/5)),a_min=2,a_max=5000))
        dict_batches_to_process = int(len(dicts) / multiprocessing_chunk_size)
        num_cpus_used = min(mp.cpu_count(), self.max_processes,  dict_batches_to_process) or 1

        with ExitStack() as stack:
            p = stack.enter_context(mp.Pool(processes=num_cpus_used))

            logger.info(
                f"Got ya {num_cpus_used} parallel workers to convert dict chunks to datasets (chunksize = {multiprocessing_chunk_size})..."
            )
            log_ascii_workers(num_cpus_used, logger)

            results = p.imap(
                partial(self._multiproc, processor=self.processor),
                grouper(dicts, multiprocessing_chunk_size),
                chunksize=1,
            )

            datasets = []
            with tqdm(total=len(dicts), unit=' Dicts') as pbar:
                for dataset, tensor_names in results:
                    datasets.append(dataset)
                    pbar.update(multiprocessing_chunk_size)
            
            concat_datasets = ConcatDataset(datasets)
            return concat_datasets, tensor_names