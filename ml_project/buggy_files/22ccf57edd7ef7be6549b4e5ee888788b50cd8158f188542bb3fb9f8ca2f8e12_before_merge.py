    def __init__(
        self,
        language: str = None,
        dim: int = 50,
        syllables: int = 100000,
        cache_dir=Path(flair.cache_root) / "embeddings",
        model_file_path: Path = None,
        embedding_file_path: Path = None,
        **kwargs,
    ):
        """
        Initializes BP embeddings. Constructor downloads required files if not there.
        """
        if language:
            self.name: str = f"bpe-{language}-{syllables}-{dim}"
        else:
            assert (
                model_file_path is not None and embedding_file_path is not None
            ), "Need to specify model_file_path and embedding_file_path if no language is given in BytePairEmbeddings(...)"
            dim=None

        self.embedder = BPEmb(
            lang=language,
            vs=syllables,
            dim=dim,
            cache_dir=cache_dir,
            model_file=model_file_path,
            emb_file=embedding_file_path,
            **kwargs,
        )

        if not language:
            self.name: str = f"bpe-custom-{self.embedder.vs}-{self.embedder.dim}"
        self.static_embeddings = True

        self.__embedding_length: int = self.embedder.emb.vector_size * 2
        super().__init__()