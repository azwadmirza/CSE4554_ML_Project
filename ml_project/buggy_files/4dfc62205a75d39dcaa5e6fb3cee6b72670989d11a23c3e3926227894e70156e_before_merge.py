    def get_similarities(self, query):
        """Get similarity between `query` and current index instance.

        Warnings
        --------
        Do not use this function directly; use the self[query] syntax instead.

        Parameters
        ----------
        query : {list of (int, number), iterable of list of (int, number), :class:`scipy.sparse.csr_matrix`
            Document or collection of documents.

        Return
        ------
        :class:`numpy.ndarray`
            Similarity matrix.

        """
        if isinstance(query, numpy.ndarray):
            # Convert document indexes to actual documents.
            query = [self.corpus[i] for i in query]

        if not query or not isinstance(query[0], list):
            query = [query]

        n_queries = len(query)
        result = []
        for qidx in range(n_queries):
            # Compute similarity for each query.
            qresult = [self.w2v_model.wmdistance(document, query[qidx]) for document in self.corpus]
            qresult = numpy.array(qresult)
            qresult = 1. / (1. + qresult)  # Similarity is the negative of the distance.

            # Append single query result to list of all results.
            result.append(qresult)

        if len(result) == 1:
            # Only one query.
            result = result[0]
        else:
            result = numpy.array(result)

        return result