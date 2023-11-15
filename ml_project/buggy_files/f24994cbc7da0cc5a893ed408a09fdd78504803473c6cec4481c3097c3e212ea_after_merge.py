    def diff(self, other, distance="kullback_leibler", num_words=100, n_ann_terms=10, normed=True):
        """
        Calculate difference topic2topic between two Lda models
        `other` instances of `LdaMulticore` or `LdaModel`
        `distance` is function that will be applied to calculate difference between any topic pair.
        Available values: `kullback_leibler`, `hellinger` and `jaccard`
        `num_words` is quantity of most relevant words that used if distance == `jaccard` (also used for annotation)
        `n_ann_terms` is max quantity of words in intersection/symmetric difference between topics (used for annotation)
        Returns a matrix Z with shape (m1.num_topics, m2.num_topics), where Z[i][j] - difference between topic_i and topic_j
        and matrix annotation with shape (m1.num_topics, m2.num_topics, 2, None),
        where:

            annotation[i][j] = [[`int_1`, `int_2`, ...], [`diff_1`, `diff_2`, ...]] and
            `int_k` is word from intersection of `topic_i` and `topic_j` and
            `diff_l` is word from symmetric difference of `topic_i` and `topic_j`
            `normed` is a flag. If `true`, matrix Z will be normalized

        Example:

        >>> m1, m2 = LdaMulticore.load(path_1), LdaMulticore.load(path_2)
        >>> mdiff, annotation = m1.diff(m2)
        >>> print(mdiff) # get matrix with difference for each topic pair from `m1` and `m2`
        >>> print(annotation) # get array with positive/negative words for each topic pair from `m1` and `m2`

        """

        distances = {
            "kullback_leibler": kullback_leibler,
            "hellinger": hellinger,
            "jaccard": jaccard_distance,
        }

        if distance not in distances:
            valid_keys = ", ".join("`{}`".format(x) for x in distances.keys())
            raise ValueError("Incorrect distance, valid only {}".format(valid_keys))

        if not isinstance(other, self.__class__):
            raise ValueError("The parameter `other` must be of type `{}`".format(self.__name__))

        distance_func = distances[distance]
        d1, d2 = self.state.get_lambda(), other.state.get_lambda()
        t1_size, t2_size = d1.shape[0], d2.shape[0]

        fst_topics = [{w for (w, _) in self.show_topic(topic, topn=num_words)} for topic in xrange(t1_size)]
        snd_topics = [{w for (w, _) in other.show_topic(topic, topn=num_words)} for topic in xrange(t2_size)]

        if distance == "jaccard":
            d1, d2 = fst_topics, snd_topics

        z = np.zeros((t1_size, t2_size))
        for topic1 in range(t1_size):
            for topic2 in range(t2_size):
                z[topic1][topic2] = distance_func(d1[topic1], d2[topic2])

        if normed:
            if np.abs(np.max(z)) > 1e-8:
                z /= np.max(z)

        annotation = [[None] * t1_size for _ in range(t2_size)]

        for topic1 in range(t1_size):
            for topic2 in range(t2_size):
                pos_tokens = fst_topics[topic1] & snd_topics[topic2]
                neg_tokens = fst_topics[topic1].symmetric_difference(snd_topics[topic2])

                pos_tokens = sample(pos_tokens, min(len(pos_tokens), n_ann_terms))
                neg_tokens = sample(neg_tokens, min(len(neg_tokens), n_ann_terms))

                annotation[topic1][topic2] = [pos_tokens, neg_tokens]

        return z, annotation