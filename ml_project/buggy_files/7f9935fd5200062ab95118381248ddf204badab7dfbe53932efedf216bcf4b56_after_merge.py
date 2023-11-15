    def bound(self, chunk, chunk_doc_idx=None, subsample_ratio=1.0, author2doc=None, doc2author=None):
        """Estimate the variational bound of documents from `corpus`.

        :math:`\mathbb{E_{q}}[\log p(corpus)] - \mathbb{E_{q}}[\log q(corpus)]`

        Notes
        -----
        There are basically two use cases of this method:

        #. `chunk` is a subset of the training corpus, and `chunk_doc_idx` is provided,
           indicating the indexes of the documents in the training corpus.
        #. `chunk` is a test set (held-out data), and `author2doc` and `doc2author` corresponding to this test set
           are provided. There must not be any new authors passed to this method, `chunk_doc_idx` is not needed
           in this case.

        Parameters
        ----------
        chunk : iterable of list of (int, float)
            Corpus in BoW format.
        chunk_doc_idx : numpy.ndarray, optional
            Assigns the value for document index.
        subsample_ratio : float, optional
            Used for calculation of word score for estimation of variational bound.
        author2doc : dict of (str, list of int), optinal
            A dictionary where keys are the names of authors and values are lists of documents that the author
            contributes to.
        doc2author : dict of (int, list of str), optional
            A dictionary where the keys are document IDs and the values are lists of author names.

        Returns
        -------
        float
            Value of variational bound score.

        """
        # TODO: enable evaluation of documents with new authors. One could, for example, make it
        # possible to pass a list of documents to self.inference with no author dictionaries,
        # assuming all the documents correspond to one (unseen) author, learn the author's
        # gamma, and return gamma (without adding it to self.state.gamma). Of course,
        # collect_sstats should be set to false, so that the model is not updated w.r.t. these
        # new documents.

        _lambda = self.state.get_lambda()
        Elogbeta = dirichlet_expectation(_lambda)
        expElogbeta = np.exp(Elogbeta)

        gamma = self.state.gamma

        if author2doc is None and doc2author is None:
            # Evaluating on training documents (chunk of self.corpus).
            author2doc = self.author2doc
            doc2author = self.doc2author

            if not chunk_doc_idx:
                # If author2doc and doc2author are not provided, chunk is assumed to be a subset of
                # self.corpus, and chunk_doc_idx is thus required.
                raise ValueError(
                    'Either author dictionaries or chunk_doc_idx must be provided. '
                    'Consult documentation of bound method.'
                )
        elif author2doc is not None and doc2author is not None:
            # Training on held-out documents (documents not seen during training).
            # All authors in dictionaries must still be seen during training.
            for a in author2doc.keys():
                if not self.author2doc.get(a):
                    raise ValueError('bound cannot be called with authors not seen during training.')

            if chunk_doc_idx:
                raise ValueError(
                    'Either author dictionaries or chunk_doc_idx must be provided, not both. '
                    'Consult documentation of bound method.'
                )
        else:
            raise ValueError(
                'Either both author2doc and doc2author should be provided, or neither. '
                'Consult documentation of bound method.'
            )

        Elogtheta = dirichlet_expectation(gamma)
        expElogtheta = np.exp(Elogtheta)

        word_score = 0.0
        theta_score = 0.0
        for d, doc in enumerate(chunk):
            if chunk_doc_idx:
                doc_no = chunk_doc_idx[d]
            else:
                doc_no = d
            # Get all authors in current document, and convert the author names to integer IDs.
            authors_d = np.array([self.author2id[a] for a in self.doc2author[doc_no]], dtype=np.integer)
            ids = np.array([id for id, _ in doc], dtype=np.integer)  # Word IDs in doc.
            cts = np.array([cnt for _, cnt in doc], dtype=np.integer)  # Word counts.

            if d % self.chunksize == 0:
                logger.debug("bound: at document #%i in chunk", d)

            # Computing the bound requires summing over expElogtheta[a, k] * expElogbeta[k, v], which
            # is the same computation as in normalizing phi.
            phinorm = self.compute_phinorm(expElogtheta[authors_d, :], expElogbeta[:, ids])
            word_score += np.log(1.0 / len(authors_d)) * sum(cts) + cts.dot(np.log(phinorm))

        # Compensate likelihood for when `chunk` above is only a sample of the whole corpus. This ensures
        # that the likelihood is always roughly on the same scale.
        word_score *= subsample_ratio

        # E[log p(theta | alpha) - log q(theta | gamma)]
        for a in author2doc.keys():
            a = self.author2id[a]
            theta_score += np.sum((self.alpha - gamma[a, :]) * Elogtheta[a, :])
            theta_score += np.sum(gammaln(gamma[a, :]) - gammaln(self.alpha))
            theta_score += gammaln(np.sum(self.alpha)) - gammaln(np.sum(gamma[a, :]))

        # theta_score is rescaled in a similar fashion.
        # TODO: treat this in a more general way, similar to how it is done with word_score.
        theta_score *= self.num_authors / len(author2doc)

        # E[log p(beta | eta) - log q (beta | lambda)]
        beta_score = 0.0
        beta_score += np.sum((self.eta - _lambda) * Elogbeta)
        beta_score += np.sum(gammaln(_lambda) - gammaln(self.eta))
        sum_eta = np.sum(self.eta)
        beta_score += np.sum(gammaln(sum_eta) - gammaln(np.sum(_lambda, 1)))

        total_score = word_score + theta_score + beta_score

        return total_score