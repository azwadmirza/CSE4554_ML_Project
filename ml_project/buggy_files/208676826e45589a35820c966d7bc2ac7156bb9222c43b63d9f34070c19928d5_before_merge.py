    def __init__(self, classifier, max_iter=1, finite_diff=1e-6, eps=.1):
        """
        Create a VirtualAdversarialMethod instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param eps: Attack step (max input variation).
        :type eps: `float`
        :param finite_diff: The finite difference parameter.
        :type finite_diff: `float`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        """
        super(VirtualAdversarialMethod, self).__init__(classifier)

        kwargs = {'finite_diff': finite_diff, 'eps': eps, 'max_iter': max_iter}
        self.set_params(**kwargs)