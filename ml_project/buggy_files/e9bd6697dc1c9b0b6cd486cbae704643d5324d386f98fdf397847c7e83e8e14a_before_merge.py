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

        dict_batches_to_process = int(len(dicts) / self.multiprocessing_chunk_size)
        num_cpus = min(mp.cpu_count(), dict_batches_to_process) or 1

        with ExitStack() as stack:
            p = stack.enter_context(mp.Pool(processes=num_cpus))

            logger.info(
                f"Got ya {num_cpus} parallel workers to do inference on {len(dicts)}dicts (chunksize = {self.multiprocessing_chunk_size})..."
            )
            log_ascii_workers(num_cpus, logger)

            results = p.imap(
                partial(self._multiproc, processor=self.processor, rest_api_schema=rest_api_schema),
                grouper(dicts, self.multiprocessing_chunk_size),
                1,
            )

            preds_all = []
            with tqdm(total=len(dicts), unit=" Dicts") as pbar:
                for dataset, tensor_names, sample in results:
                    preds_all.extend(self._run_inference(dataset, tensor_names, sample))
                    pbar.update(self.multiprocessing_chunk_size)

        return preds_all