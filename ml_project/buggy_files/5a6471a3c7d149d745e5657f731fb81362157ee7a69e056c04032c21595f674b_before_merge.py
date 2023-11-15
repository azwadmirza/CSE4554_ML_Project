    def _create_sequence(
        self, attribute: Text, all_tokens: List[List[Text]]
    ) -> List[scipy.sparse.coo_matrix]:
        X = []

        for i, tokens in enumerate(all_tokens):
            # vectorizer.transform returns a sparse matrix of size
            # [n_samples, n_features]
            # set input to list of tokens if sequence should be returned
            # otherwise join all tokens to a single string and pass that as a list
            tokens_without_cls = tokens
            if attribute in [TEXT_ATTRIBUTE, RESPONSE_ATTRIBUTE]:
                tokens_without_cls = tokens[:-1]

            seq_vec = self.vectorizers[attribute].transform(tokens_without_cls)
            seq_vec.sort_indices()

            if attribute in [TEXT_ATTRIBUTE, RESPONSE_ATTRIBUTE]:
                tokens_text = [" ".join(tokens_without_cls)]
                cls_vec = self.vectorizers[attribute].transform(tokens_text)
                cls_vec.sort_indices()

                x = scipy.sparse.vstack([seq_vec, cls_vec])
            else:
                x = seq_vec

            X.append(x.tocoo())

        return X