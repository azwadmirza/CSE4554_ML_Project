    def inference(self, chunk, author2doc, doc2author, rhot, collect_sstats=False, chunk_doc_idx=None):
        """Give a `chunk` of sparse document vectors, update gamma for each author corresponding to the `chuck`.

        Warnings
        --------
        The whole input chunk of document is assumed to fit in RAM, chunking of a large corpus must be done earlier
        in the pipeline.

        Avoids computing the `phi` variational parameter directly using the
        optimization presented in `Lee, Seung: "Algorithms for non-negative matrix factorization", NIPS 2001
        <https://papers.nips.cc/paper/1861-algorithms-for-non-negative-matrix-factorization.pdf>`_.

        Parameters
        ----------
        chunk : iterable of list of (int, float)
            Corpus in BoW format.
        author2doc : dict of (str, list of int), optional
            A dictionary where keys are the names of authors and values are lists of document IDs that the author
            contributes to.
        doc2author : dict of (int, list of str), optional
            A dictionary where the keys are document IDs and the values are lists of author names.
        rhot : float
            Value of rho for conducting inference on documents.
        collect_sstats : boolean, optional
            If True - collect sufficient statistics needed to update the model's topic-word distributions, and return
            `(gamma_chunk, sstats)`. Otherwise, return `(gamma_chunk, None)`. `gamma_chunk` is of shape
            `len(chunk_authors) x self.num_topics`,where `chunk_authors` is the number of authors in the documents in
            the current chunk.
        chunk_doc_idx : numpy.ndarray, optional
            Assigns the value for document index.

        Returns
        -------
        (numpy.ndarray, numpy.ndarray)
            gamma_chunk and sstats (if `collect_sstats == True`, otherwise - None)

        """
        try:
            len(chunk)
        except TypeError:
            # convert iterators/generators to plain list, so we have len() etc.
            chunk = list(chunk)
        if len(chunk) > 1:
            logger.debug("performing inference on a chunk of %i documents", len(chunk))

        # Initialize the variational distribution q(theta|gamma) for the chunk
        if collect_sstats:
            sstats = np.zeros_like(self.expElogbeta)
        else:
            sstats = None
        converged = 0

        # Stack all the computed gammas into this output array.
        gamma_chunk = np.zeros((0, self.num_topics))

        # Now, for each document d update gamma and phi w.r.t. all authors in those documents.
        for d, doc in enumerate(chunk):
            if chunk_doc_idx is not None:
                doc_no = chunk_doc_idx[d]
            else:
                doc_no = d
            # Get the IDs and counts of all the words in the current document.
            # TODO: this is duplication of code in LdaModel. Refactor.
            if doc and not isinstance(doc[0][0], six.integer_types + (np.integer,)):
                # make sure the term IDs are ints, otherwise np will get upset
                ids = [int(idx) for idx, _ in doc]
            else:
                ids = [idx for idx, _ in doc]
            ids = np.array(ids, dtype=np.integer)
            cts = np.array([cnt for _, cnt in doc], dtype=np.integer)

            # Get all authors in current document, and convert the author names to integer IDs.
            authors_d = np.array([self.author2id[a] for a in self.doc2author[doc_no]], dtype=np.integer)

            gammad = self.state.gamma[authors_d, :]  # gamma of document d before update.
            tilde_gamma = gammad.copy()  # gamma that will be updated.

            # Compute the expectation of the log of the Dirichlet parameters theta and beta.
            Elogthetad = dirichlet_expectation(tilde_gamma)
            expElogthetad = np.exp(Elogthetad)
            expElogbetad = self.expElogbeta[:, ids]

            # Compute the normalizing constant of phi for the current document.
            phinorm = self.compute_phinorm(expElogthetad, expElogbetad)

            # Iterate between gamma and phi until convergence
            for _ in xrange(self.iterations):
                lastgamma = tilde_gamma.copy()

                # Update gamma.
                # phi is computed implicitly below,
                for ai, a in enumerate(authors_d):
                    tilde_gamma[ai, :] = self.alpha + len(self.author2doc[self.id2author[a]])\
                        * expElogthetad[ai, :] * np.dot(cts / phinorm, expElogbetad.T)

                # Update gamma.
                # Interpolation between document d's "local" gamma (tilde_gamma),
                # and "global" gamma (gammad).
                tilde_gamma = (1 - rhot) * gammad + rhot * tilde_gamma

                # Update Elogtheta and Elogbeta, since gamma and lambda have been updated.
                Elogthetad = dirichlet_expectation(tilde_gamma)
                expElogthetad = np.exp(Elogthetad)

                # Update the normalizing constant in phi.
                phinorm = self.compute_phinorm(expElogthetad, expElogbetad)

                # Check for convergence.
                # Criterion is mean change in "local" gamma.
                meanchange_gamma = np.mean(abs(tilde_gamma - lastgamma))
                gamma_condition = meanchange_gamma < self.gamma_threshold
                if gamma_condition:
                    converged += 1
                    break
            # End of iterations loop.

            # Store the updated gammas in the model state.
            self.state.gamma[authors_d, :] = tilde_gamma

            # Stack the new gammas into the output array.
            gamma_chunk = np.vstack([gamma_chunk, tilde_gamma])

            if collect_sstats:
                # Contribution of document d to the expected sufficient
                # statistics for the M step.
                expElogtheta_sum_a = expElogthetad.sum(axis=0)
                sstats[:, ids] += np.outer(expElogtheta_sum_a.T, cts / phinorm)

        if len(chunk) > 1:
            logger.debug(
                "%i/%i documents converged within %i iterations",
                converged, len(chunk), self.iterations
            )

        if collect_sstats:
            # This step finishes computing the sufficient statistics for the
            # M step, so that
            # sstats[k, w] = \sum_d n_{dw} * \sum_a phi_{dwak}
            # = \sum_d n_{dw} * exp{Elogtheta_{ak} + Elogbeta_{kw}} / phinorm_{dw}.
            sstats *= self.expElogbeta
        return gamma_chunk, sstats