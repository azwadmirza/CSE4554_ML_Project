    def fit_lda_seq(self, corpus, lda_inference_max_iter, em_min_iter, em_max_iter, chunksize):
        """
        fit an lda sequence model:
            for each time period:
                set up lda model with E[log p(w|z)] and \alpha

                for each document:
                    perform posterior inference
                    update sufficient statistics/likelihood

            maximize topics

       """
        LDASQE_EM_THRESHOLD = 1e-4
        # if bound is low, then we increase iterations.
        LOWER_ITER = 10
        ITER_MULT_LOW = 2
        MAX_ITER = 500

        num_topics = self.num_topics
        vocab_len = self.vocab_len
        data_len = self.num_time_slices
        corpus_len = self.corpus_len

        bound = 0
        convergence = LDASQE_EM_THRESHOLD + 1
        iter_ = 0

        while iter_ < em_min_iter or ((convergence > LDASQE_EM_THRESHOLD) and iter_ <= em_max_iter):

            logger.info(" EM iter %i", iter_)
            logger.info("E Step")
            # TODO: bound is initialized to 0
            old_bound = bound

            # initiate sufficient statistics
            topic_suffstats = []
            for topic in range(0, num_topics):
                topic_suffstats.append(np.resize(np.zeros(vocab_len * data_len), (vocab_len, data_len)))

            # set up variables
            gammas = np.resize(np.zeros(corpus_len * num_topics), (corpus_len, num_topics))
            lhoods = np.resize(np.zeros(corpus_len * num_topics + 1), (corpus_len, num_topics + 1))
            # compute the likelihood of a sequential corpus under an LDA
            # seq model and find the evidence lower bound. This is the E - Step
            bound, gammas = self.lda_seq_infer(corpus, topic_suffstats, gammas, lhoods, iter_, lda_inference_max_iter, chunksize)
            self.gammas = gammas

            logger.info("M Step")

            # fit the variational distribution. This is the M - Step
            topic_bound = self.fit_lda_seq_topics(topic_suffstats)
            bound += topic_bound

            if ((bound - old_bound) < 0):
                # if max_iter is too low, increase iterations.
                if lda_inference_max_iter < LOWER_ITER:
                    lda_inference_max_iter *= ITER_MULT_LOW
                logger.info("Bound went down, increasing iterations to %i", lda_inference_max_iter)

            # check for convergence
            convergence = np.fabs((bound - old_bound) / old_bound)

            if convergence < LDASQE_EM_THRESHOLD:

                lda_inference_max_iter = MAX_ITER
                logger.info("Starting final iterations, max iter is %i", lda_inference_max_iter)
                convergence = 1.0

            logger.info("iteration %i iteration lda seq bound is %f convergence is %f", iter_, bound, convergence)

            iter_ += 1

        return bound