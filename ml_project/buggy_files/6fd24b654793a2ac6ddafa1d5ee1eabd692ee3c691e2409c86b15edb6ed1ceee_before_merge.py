    def load(
        cls,
        model_name_or_path,
        batch_size=4,
        gpu=False,
        task_type=None,
        return_class_probs=False,
        strict=True,
        max_seq_len=256,
        doc_stride=128,
        extraction_layer=None,
        extraction_strategy=None
    ):
        """
        Load an Inferencer incl. all relevant components (model, tokenizer, processor ...) either by

        1. specifying a public name from transformers' model hub (https://huggingface.co/models)
        2. or pointing to a local directory it is saved in.

        :param model_name_or_path: Local directory or public name of the model to load.
        :type model_name_or_path: str
        :param batch_size: Number of samples computed once per batch
        :type batch_size: int
        :param gpu: If GPU shall be used
        :type gpu: bool
        :param task_type: Type of task the model should be used for. Currently supporting:
                          "embeddings", "question_answering", "text_classification", "ner". More coming soon...
        :param task_type: str
        :param strict: whether to strictly enforce that the keys loaded from saved model match the ones in
                       the PredictionHead (see torch.nn.module.load_state_dict()).
                       Set to `False` for backwards compatibility with PHs saved with older version of FARM.
        :type strict: bool
        :param max_seq_len: maximum length of one text sample
        :type max_seq_len: int
        :param doc_stride: Only QA: When input text is longer than max_seq_len it gets split into parts, strided by doc_stride
        :type doc_stride: int
        :param extraction_strategy: Strategy to extract vectors. Choices: 'cls_token' (sentence vector), 'reduce_mean'
                               (sentence vector), reduce_max (sentence vector), 'per_token' (individual token vectors)
        :type extraction_strategy: str
        :param extraction_layer: number of layer from which the embeddings shall be extracted. Default: -1 (very last layer).
        :type extraction_layer: int
        :return: An instance of the Inferencer.

        """

        device, n_gpu = initialize_device_settings(use_cuda=gpu, local_rank=-1, use_amp=None)
        name = os.path.basename(model_name_or_path)

        # a) either from local dir
        if os.path.exists(model_name_or_path):
            model = BaseAdaptiveModel.load(load_dir=model_name_or_path, device=device, strict=strict)
            if task_type == "embeddings":
                processor = InferenceProcessor.load_from_dir(model_name_or_path)
            else:
                processor = Processor.load_from_dir(model_name_or_path)

        # b) or from remote transformers model hub
        else:
            logger.info(f"Could not find `{model_name_or_path}` locally. Try to download from model hub ...")
            if not task_type:
                raise ValueError("Please specify the 'task_type' of the model you want to load from transformers. "
                                 "Valid options for arg `task_type`:"
                                 "'question_answering', 'embeddings', 'text_classification', 'ner'")

            model = AdaptiveModel.convert_from_transformers(model_name_or_path, device, task_type)
            config = AutoConfig.from_pretrained(model_name_or_path)
            tokenizer = Tokenizer.load(model_name_or_path)

            # TODO infer task_type automatically from config (if possible)
            if task_type == "question_answering":
                processor = SquadProcessor(
                    tokenizer=tokenizer,
                    max_seq_len=max_seq_len,
                    label_list=["start_token", "end_token"],
                    metric="squad",
                    data_dir=None,
                    doc_stride=doc_stride
                )
            elif task_type == "embeddings":
                processor = InferenceProcessor(tokenizer=tokenizer, max_seq_len=max_seq_len)

            elif task_type == "text_classification":
                label_list = list(config.id2label[id] for id in range(len(config.id2label)))
                processor = TextClassificationProcessor(tokenizer=tokenizer,
                                                        max_seq_len=max_seq_len,
                                                        data_dir=None,
                                                        label_list=label_list,
                                                        label_column_name="label",
                                                        metric="acc",
                                                        quote_char='"',
                                                        )
            elif task_type == "ner":
                label_list = list(config.label2id.keys())
                processor = NERProcessor(
                    tokenizer=tokenizer, max_seq_len=max_seq_len, data_dir=None, metric="seq_f1",
                    label_list=label_list
                )
            else:
                raise ValueError(f"`task_type` {task_type} is not supported yet. "
                                 f"Valid options for arg `task_type`: 'question_answering', "
                                 f"'embeddings', 'text_classification', 'ner'")

        return cls(
            model,
            processor,
            task_type=task_type,
            batch_size=batch_size,
            gpu=gpu,
            name=name,
            return_class_probs=return_class_probs,
            extraction_strategy=extraction_strategy,
            extraction_layer=extraction_layer
        )