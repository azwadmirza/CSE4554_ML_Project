    def __init__(self, classifier, norm=np.inf, eps=.3, eps_step=0.1, max_iter=20, targeted=False, random_init=False):
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
        :param targeted: Should the attack target one specific class
        :type targeted: `bool`
        :param random_init: Whether to start at the original input or a random point within the epsilon ball
        :type random_init: `bool`
        """
        super(BasicIterativeMethod, self).__init__(classifier, norm=norm, eps=eps, targeted=targeted,
                                                   random_init=random_init)

        if eps_step > eps:
            raise ValueError('The iteration step `eps_step` has to be smaller than the total attack `eps`.')
        self.eps_step = eps_step

        if max_iter <= 0:
            raise ValueError('The number of iterations `max_iter` has to be a positive integer.')
        self.max_iter = int(max_iter)

        self._project = False