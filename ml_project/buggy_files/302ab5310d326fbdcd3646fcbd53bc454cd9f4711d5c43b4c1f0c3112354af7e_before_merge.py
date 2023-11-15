    def __init__(
            self,
            model: str = "bert-base-uncased",
            layers: str = "all",
            subtoken_pooling: str = "first",
            layer_mean: bool = True,
            fine_tune: bool = False,
            allow_long_sentences: bool = True,
            use_context: Union[bool, int] = False,
            **kwargs
    ):
        """
        Bidirectional transformer embeddings of words from various transformer architectures.
        :param model: name of transformer model (see https://huggingface.co/transformers/pretrained_models.html for
        options)
        :param layers: string indicating which layers to take for embedding (-1 is topmost layer)
        :param subtoken_pooling: how to get from token piece embeddings to token embedding. Either take the first
        subtoken ('first'), the last subtoken ('last'), both first and last ('first_last') or a mean over all ('mean')
        :param layer_mean: If True, uses a scalar mix of layers as embedding
        :param fine_tune: If True, allows transformers to be fine-tuned during training
        """
        super().__init__()
        self.instance_parameters = self.get_instance_parameters(locals=locals())

        # temporary fix to disable tokenizer parallelism warning
        # (see https://stackoverflow.com/questions/62691279/how-to-disable-tokenizers-parallelism-true-false-warning)
        import os
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # load tokenizer and transformer model
        self.tokenizer = AutoTokenizer.from_pretrained(model, **kwargs)
        config = AutoConfig.from_pretrained(model, output_hidden_states=True, **kwargs)
        self.model = AutoModel.from_pretrained(model, config=config, **kwargs)

        self.allow_long_sentences = allow_long_sentences

        if allow_long_sentences:
            self.max_subtokens_sequence_length = self.tokenizer.model_max_length
            self.stride = self.tokenizer.model_max_length // 2
        else:
            self.max_subtokens_sequence_length = self.tokenizer.model_max_length
            self.stride = 0

        # model name
        self.name = 'transformer-word-' + str(model)

        # store whether to use context (and how much)
        if type(use_context) == bool:
            self.context_length: int = 64 if use_context else 0
        if type(use_context) == int:
            self.context_length: int = use_context

        # when initializing, embeddings are in eval mode by default
        self.model.eval()
        self.model.to(flair.device)

        # embedding parameters
        if layers == 'all':
            # send mini-token through to check how many layers the model has
            hidden_states = self.model(torch.tensor([1], device=flair.device).unsqueeze(0))[-1]
            self.layer_indexes = [int(x) for x in range(len(hidden_states))]
        else:
            self.layer_indexes = [int(x) for x in layers.split(",")]

        self.pooling_operation = subtoken_pooling
        self.layer_mean = layer_mean
        self.fine_tune = fine_tune
        self.static_embeddings = not self.fine_tune

        self.special_tokens = []
        # check if special tokens exist to circumvent error message
        if self.tokenizer._bos_token:
            self.special_tokens.append(self.tokenizer.bos_token)
        if self.tokenizer._cls_token:
            self.special_tokens.append(self.tokenizer.cls_token)

        # most models have an intial BOS token, except for XLNet, T5 and GPT2
        self.begin_offset = 1
        if type(self.tokenizer) == XLNetTokenizer:
            self.begin_offset = 0
        if type(self.tokenizer) == T5Tokenizer:
            self.begin_offset = 0
        if type(self.tokenizer) == GPT2Tokenizer:
            self.begin_offset = 0
        if type(self.tokenizer) == TransfoXLTokenizer:
            self.begin_offset = 0