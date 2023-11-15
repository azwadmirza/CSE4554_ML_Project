    def inference_from_dicts(self, dicts, rest_api_schema=False):
        """
        Runs down-stream inference using the prediction head.

        :param dicts: Samples to run inference on provided as a list of dicts. One dict per sample.
        :type dicts: [dict]
        :param rest_api_schema: whether conform to the schema used for dicts in the HTTP API for Inference.
        :type rest_api_schema: bool
        :return: dict of predictions

        """
        if self.prediction_type == "embedder":
            raise TypeError(
                "You have called inference_from_dicts for a model without any prediction head! "
                "If you want to: "
                "a) ... extract vectors from the language model: call `Inferencer.extract_vectors(...)`"
                f"b) ... run inference on a downstream task: make sure your model path {self.name} contains a saved prediction head"
            )

        num_cpus = mp.cpu_count() or 1
        dicts_per_cpu = np.ceil(len(dicts) / num_cpus)
        # automatic adjustment of multiprocessing chunksize
        # for small files (containing few dicts) we want small chunksize to ulitize all available cores but never less
        # than 2, because we need it to sample another random sentence in LM finetuning
        # for large files we want to minimize processor spawning without giving too much data to one process, so we
        # clip it at 5k
        multiprocessing_chunk_size = int(np.clip((np.ceil(dicts_per_cpu / 5)), a_min=2, a_max=5000))
        dict_batches_to_process = int(len(dicts) / multiprocessing_chunk_size)
        num_cpus_used = min(mp.cpu_count(), dict_batches_to_process) or 1

        with ExitStack() as stack:
            p = stack.enter_context(mp.Pool(processes=num_cpus_used))

            logger.info(
                f"Got ya {num_cpus_used} parallel workers to do inference on {len(dicts)}dicts (chunksize = {multiprocessing_chunk_size})..."
            )
            log_ascii_workers(num_cpus_used, logger)

            results = p.imap(
                partial(self._multiproc, processor=self.processor, rest_api_schema=rest_api_schema),
                grouper(dicts, multiprocessing_chunk_size),
                1,
            )

            preds_all = []
            with tqdm(total=len(dicts), unit=" Dicts") as pbar:
                for dataset, tensor_names, sample in results:
                    preds_all.extend(self._run_inference(dataset, tensor_names, sample))
                    pbar.update(multiprocessing_chunk_size)

        return preds_all