    def set_embedding(self, *embeddings):
        """Attaches one or more embeddings to the indexed text tokens.


        Parameters
        ----------
        embeddings : None or tuple of :class:`gluonnlp.embedding.TokenEmbedding` instances
            The embedding to be attached to the indexed tokens. If a tuple of multiple embeddings
            are provided, their embedding vectors will be concatenated for the same token.
        """

        if len(embeddings) == 1 and embeddings[0] is None:
            self._embedding = None
            return

        for embs in embeddings:
            assert isinstance(embs, emb.TokenEmbedding), \
                'The argument `embeddings` must be an instance or a list of instances of ' \
                '`gluonnlp.embedding.TokenEmbedding`.'
            assert embs.idx_to_vec is not None, \
                'For all specified `embeddings`, `embeddings.idx_to_vec` must be initialized. ' \
                'Use eg. `emb[emb.unknown_token] = nd.zeros(emsize)` to initialize, ' \
                'where `emsize` is the desired embedding dimensionality.'

        assert all([embs.unknown_token for embs in embeddings]) or \
            all([not embs.unknown_token for embs in embeddings]), \
            'Either all or none of the TokenEmbeddings must have an ' \
            'unknown_token set.'

        new_vec_len = sum(embs.idx_to_vec.shape[1] for embs in embeddings)
        # TODO(leezu): Remove once np shape is used by default
        assert len(self), 'Empty vocab not yet supported'
        new_idx_to_vec = nd.zeros(shape=(len(self), new_vec_len))

        col_start = 0
        # Concatenate all the embedding vectors in embedding.
        for embs in embeddings:
            if embs and embs.idx_to_vec is not None:
                col_end = col_start + embs.idx_to_vec.shape[1]
                # Cancatenate vectors of the unknown token.
                new_idx_to_vec[0, col_start:col_end] = embs.idx_to_vec[0]
                new_idx_to_vec[1:, col_start:col_end] = embs[self._idx_to_token[1:]]
                col_start = col_end

        self._embedding = emb.TokenEmbedding(self.unknown_token,
                                             init_unknown_vec=None,
                                             allow_extend=False,
                                             idx_to_token=self.idx_to_token,
                                             idx_to_vec=new_idx_to_vec)