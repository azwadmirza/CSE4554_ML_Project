    def __init__(self, classifier, norm=np.inf, eps=.3, eps_step=0.1, max_iter=20, targeted=False, random_init=False):
        """
        Create a :class:`ProjectedGradientDescent` instance.

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
        super(ProjectedGradientDescent, self).__init__(classifier, norm=norm, eps=eps, eps_step=eps_step,
                                                       max_iter=max_iter, targeted=targeted, random_init=random_init)

        self._project = True