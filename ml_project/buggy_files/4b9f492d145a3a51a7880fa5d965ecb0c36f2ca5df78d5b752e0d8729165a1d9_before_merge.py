def make_multilabel_classification(n_samples=100, n_features=20, n_classes=5,
                                   n_labels=2, length=50, allow_unlabeled=True,
                                   return_indicator=False, random_state=None):
    """Generate a random multilabel classification problem.

    For each sample, the generative process is:
        - pick the number of labels: n ~ Poisson(n_labels)
        - n times, choose a class c: c ~ Multinomial(theta)
        - pick the document length: k ~ Poisson(length)
        - k times, choose a word: w ~ Multinomial(theta_c)

    In the above process, rejection sampling is used to make sure that
    n is never zero or more than `n_classes`, and that the document length
    is never zero. Likewise, we reject classes which have already been chosen.

    Parameters
    ----------
    n_samples : int, optional (default=100)
        The number of samples.

    n_features : int, optional (default=20)
        The total number of features.

    n_classes : int, optional (default=5)
        The number of classes of the classification problem.

    n_labels : int, optional (default=2)
        The average number of labels per instance. Number of labels follows
        a Poisson distribution that never takes the value 0.

    length : int, optional (default=50)
        Sum of the features (number of words if documents).

    allow_unlabeled : bool, optional (default=True)
        If ``True``, some instances might not belong to any class.

    return_indicator : bool, optional (default=False),
        If ``True``, return ``Y`` in the binary indicator format, else
        return a tuple of lists of labels.

    random_state : int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used
        by `np.random`.

    Returns
    -------
    X : array of shape [n_samples, n_features]
        The generated samples.

    Y : tuple of lists or array of shape [n_samples, n_classes]
        The label sets.

    """
    generator = check_random_state(random_state)
    p_c = generator.rand(n_classes)
    p_c /= p_c.sum()
    p_w_c = generator.rand(n_features, n_classes)
    p_w_c /= np.sum(p_w_c, axis=0)

    def sample_example():
        _, n_classes = p_w_c.shape

        # pick a nonzero number of labels per document by rejection sampling
        n = n_classes + 1
        while (not allow_unlabeled and n == 0) or n > n_classes:
            n = generator.poisson(n_labels)

        # pick n classes
        y = []
        while len(y) != n:
            # pick a class with probability P(c)
            c = generator.multinomial(1, p_c).argmax()

            if not c in y:
                y.append(c)

        # pick a non-zero document length by rejection sampling
        k = 0
        while k == 0:
            k = generator.poisson(length)

        # generate a document of length k words
        x = np.zeros(n_features, dtype=int)
        for i in range(k):
            if len(y) == 0:
                # if sample does not belong to any class, generate noise word
                w = generator.randint(n_features)
            else:
                # pick a class and generate an appropriate word
                c = y[generator.randint(len(y))]
                w = generator.multinomial(1, p_w_c[:, c]).argmax()
            x[w] += 1

        return x, y

    X, Y = zip(*[sample_example() for i in range(n_samples)])

    if return_indicator:
        lb = MultiLabelBinarizer()
        Y = lb.fit([range(n_classes)]).transform(Y)
    else:
        warnings.warn('Support for the sequence of sequences multilabel '
                      'representation is being deprecated and replaced with '
                      'a sparse indicator matrix. '
                      'return_indicator wil default to True from version '
                      '0.17.',
                      DeprecationWarning)

    return np.array(X, dtype=np.float64), Y