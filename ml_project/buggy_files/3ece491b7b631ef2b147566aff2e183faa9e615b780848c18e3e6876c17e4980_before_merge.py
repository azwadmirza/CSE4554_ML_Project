    def create_embedding(self, texts: [str]):
        """
        Create embeddings for each text in a list of texts using the retrievers model (`self.embedding_model`)
        :param texts: texts to embed
        :return: list of embeddings (one per input text). Each embedding is a list of floats.
        """

        # for backward compatibility: cast pure str input
        if type(texts) == str:
            texts = [texts]
        assert type(texts) == list, "Expecting a list of texts, i.e. create_embeddings(texts=['text1',...])"

        if self.model_format == "farm":
            res = self.embedding_model.inference_from_dicts(dicts=[{"text": t} for t in texts])
            emb = [list(r["vec"]) for r in res] #cast from numpy
        elif self.model_format == "sentence_transformers":
            # text is single string, sentence-transformers needs a list of strings
            res = self.embedding_model.encode(texts)  # get back list of numpy embedding vectors
            emb = [list(r) for r in res] #cast from numpy
        return emb