    def __init__(self, classifier, norm=np.inf, eps=.3, eps_step=0.1, max_iter=20, targeted=False, random_init=False,
                 batch_size=128, expectation=None):
        """
        Create a :class:`BasicIterativeMethod` instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param norm: Order of the norm. Possible values: np.inf, 1 or 2.
        :type norm: `int`
        :param eps: Maximum perturbation that the attacker can introduce.
        :type eps: `float`
        :param eps_step: Attack step size (input variation) at each iteration.
        :type eps_step: `float`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
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
        super(BasicIterativeMethod, self).__init__(classifier, norm=norm, eps=eps, targeted=targeted,
                                                   random_init=random_init, batch_size=batch_size,
                                                   expectation=expectation)

        if eps_step > eps:
            raise ValueError('The iteration step `eps_step` has to be smaller than the total attack `eps`.')
        self.eps_step = eps_step

        if max_iter <= 0:
            raise ValueError('The number of iterations `max_iter` has to be a positive integer.')
        self.max_iter = int(max_iter)

        self._project = False