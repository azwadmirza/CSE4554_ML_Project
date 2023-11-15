    def _get_dataset(self, filename):
        dicts = self.processor.file_to_dicts(filename)
        #shuffle list of dicts here if we later want to have a random dev set splitted from train set
        if self.processor.train_filename in filename:
            if not self.processor.dev_filename:
                if self.processor.dev_split > 0.0:
                    random.shuffle(dicts)

        dict_batches_to_process = int(len(dicts) / self.multiprocessing_chunk_size)
        num_cpus = min(mp.cpu_count(), self.max_processes,  dict_batches_to_process) or 1

        with ExitStack() as stack:
            p = stack.enter_context(mp.Pool(processes=num_cpus))

            logger.info(
                f"Got ya {num_cpus} parallel workers to convert dict chunks to datasets (chunksize = {self.multiprocessing_chunk_size})..."
            )
            log_ascii_workers(num_cpus, logger)

            results = p.imap(
                partial(self._multiproc, processor=self.processor),
                grouper(dicts, self.multiprocessing_chunk_size),
                chunksize=1,
            )

            datasets = []
            with tqdm(total=len(dicts), unit=' Dicts') as pbar:
                for dataset, tensor_names in results:
                    datasets.append(dataset)
                    pbar.update(self.multiprocessing_chunk_size)
            
            concat_datasets = ConcatDataset(datasets)
            return concat_datasets, tensor_names