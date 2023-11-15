    def get_similarities(self, query):
        """Get similarity between `query` and current index instance.

        Warnings
        --------
        Do not use this function directly; use the self[query] syntax instead.

        Parameters
        ----------
        query : {list of (int, number), iterable of list of (int, number)
            Document or collection of documents.

        Return
        ------
        :class:`numpy.ndarray`
            Similarity matrix.

        """

        is_corpus, query = utils.is_corpus(query)
        if not is_corpus:
            if isinstance(query, numpy.ndarray):
                # Convert document indexes to actual documents.
                query = [self.corpus[i] for i in query]
            else:
                query = [query]

        result = []
        for query_document in query:
            # Compute similarity for each query.
            qresult = [matutils.softcossim(query_document, corpus_document, self.similarity_matrix)
                       for corpus_document in self.corpus]
            qresult = numpy.array(qresult)

            # Append single query result to list of all results.
            result.append(qresult)

        if is_corpus:
            result = numpy.array(result)
        else:
            result = result[0]

        return result