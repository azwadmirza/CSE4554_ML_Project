    def __init__(self, classifier, norm=np.inf, eps=.3, targeted=False, random_init=False, batch_size=128,
                 expectation=None):
        """
        Create a :class:`FastGradientMethod` instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param norm: Order of the norm. Possible values: np.inf, 1 or 2.
        :type norm: `int`
        :param eps: Attack step size (input variation)
        :type eps: `float`
        :param targeted: Should the attack target one specific class
        :type targeted: `bool`
        :param random_init: Whether to start at the original input or a random point within the epsilon ball
        :type random_init: `bool`
        :param batch_size: Batch size
        :type batch_size: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        super(FastGradientMethod, self).__init__(classifier, expectation=expectation)

        self.norm = norm
        self.eps = eps
        self.targeted = targeted
        self.random_init = random_init
        self.batch_size = batch_size