    def __init__(
            self,
            model_name_or_path: str = "facebook/rag-token-nq",
            retriever: Optional[DensePassageRetriever] = None,
            generator_type: RAGeneratorType = RAGeneratorType.TOKEN,
            top_k_answers: int = 2,
            max_length: int = 200,
            min_length: int = 2,
            num_beams: int = 2,
            embed_title: bool = True,
            prefix: Optional[str] = None,
            use_gpu: bool = True,
    ):
        """
        Load a RAG model from Transformers along with passage_embedding_model.
        See https://huggingface.co/transformers/model_doc/rag.html for more details

        :param model_name_or_path: Directory of a saved model or the name of a public model e.g.
                                   'facebook/rag-token-nq', 'facebook/rag-sequence-nq'.
                                   See https://huggingface.co/models for full list of available models.
        :param retriever: `DensePassageRetriever` used to embedded passage
        :param generator_type: Which RAG generator implementation to use? RAG-TOKEN or RAG-SEQUENCE
        :param top_k_answers: Number of independently generated text to return
        :param max_length: Maximum length of generated text
        :param min_length: Minimum length of generated text
        :param num_beams: Number of beams for beam search. 1 means no beam search.
        :param embed_title: Embedded the title of passage while generating embedding
        :param prefix: The prefix used by the generator's tokenizer.
        :param use_gpu: Whether to use GPU (if available)
        """

        self.model_name_or_path = model_name_or_path
        self.max_length = max_length
        self.min_length = min_length
        self.generator_type = generator_type
        self.num_beams = num_beams
        self.embed_title = embed_title
        self.prefix = prefix
        self.retriever = retriever

        if top_k_answers > self.num_beams:
            top_k_answers = self.num_beams
            logger.warning(f'top_k_answers value should not be greater than num_beams, hence setting it to {num_beams}')

        self.top_k_answers = top_k_answers

        if use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
            raise AttributeError("Currently RAGenerator does not support GPU, try with use_gpu=False")
        else:
            self.device = torch.device("cpu")

        self.tokenizer = RagTokenizer.from_pretrained(model_name_or_path)

        if self.generator_type == RAGeneratorType.SEQUENCE:
            raise NotImplementedError("RagSequenceForGeneration is not implemented yet")
            # TODO: Enable when transformers have it. Refer https://github.com/huggingface/transformers/issues/7905
            # Also refer refer https://github.com/huggingface/transformers/issues/7829
            # self.model = RagSequenceForGeneration.from_pretrained(model_name_or_path)
        else:
            self.model = RagTokenForGeneration.from_pretrained(model_name_or_path)