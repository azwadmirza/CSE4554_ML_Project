    def load(
        cls,
        load_dir,
        batch_size=4,
        gpu=False,
        embedder_only=False,
        return_class_probs=False,
        multiprocessing_chunk_size=100,
    ):
        """
        Initializes Inferencer from directory with saved model.

        :param load_dir: Directory where the saved model is located.
        :type load_dir: str
        :param batch_size: Number of samples computed once per batch
        :type batch_size: int
        :param gpu: If GPU shall be used
        :type gpu: bool
        :param embedder_only: If true, a faster processor (InferenceProcessor) is loaded. This should only be used
        for extracting embeddings (no downstream predictions).
        :type embedder_only: bool
        :param multiprocessing_chunk_size: chunksize param for Python Multiprocessing imap().
        :type multiprocessing_chunk_size: int
        :return: An instance of the Inferencer.
        """

        device, n_gpu = initialize_device_settings(use_cuda=gpu, local_rank=-1, fp16=False)

        model = AdaptiveModel.load(load_dir, device)
        if embedder_only:
            # model.prediction_heads = []
            processor = InferenceProcessor.load_from_dir(load_dir)
        else:
            processor = Processor.load_from_dir(load_dir)

        name = os.path.basename(load_dir)
        return cls(
            model,
            processor,
            batch_size=batch_size,
            gpu=gpu,
            name=name,
            return_class_probs=return_class_probs,
            multiprocessing_chunk_size=multiprocessing_chunk_size,
        )